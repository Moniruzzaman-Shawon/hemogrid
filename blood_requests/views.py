from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count
from .models import BloodRequest, DonationHistory
from .serializers import (
    BloodRequestSerializer,
    DonationHistorySerializer,
    BloodRequestStatusSerializer,
    AdminBloodRequestSerializer,
    AcceptBloodRequestSerializer
)
from accounts.models import User
from notifications.models import Notification
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings

# -------------------------
# Permissions
# -------------------------
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.role=='admin')

# -------------------------
# Blood Requests
# -------------------------
class BloodRequestCreateView(generics.CreateAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        # Make user a donor if not already
        if user.role != "donor":
            user.role = "donor"
            # optional: mark as available using correct choice value
            user.availability_status = 'available'
            user.save()

        blood_request = serializer.save(requester=user)

        # Trigger notification to nearby donors
        nearby_donors = User.objects.filter(
            role='donor',
            is_verified=True,
            availability_status=True,
            blood_group=blood_request.blood_group
        )
        for donor in nearby_donors:
            Notification.objects.create(
                user=donor,
                message=f"New blood request for {blood_request.blood_group} near you!"
            )


class BloodRequestListView(generics.ListAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['blood_group', 'urgency', 'status']
    search_fields = ['location', 'details']
    ordering_fields = ['created_at']

    def get_queryset(self):
        # Avoid DB side effects during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return BloodRequest.objects.none()
        now = timezone.now()
        # Auto-close expired requests
        BloodRequest.objects.filter(expires_at__lt=now, is_active=True).update(is_active=False)
        return BloodRequest.objects.filter(is_active=True).exclude(requester=self.request.user)

class AcceptBloodRequestView(generics.GenericAPIView):
    queryset = BloodRequest.objects.all()
    serializer_class = AcceptBloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    
    def post(self, request, pk):
        blood_request = get_object_or_404(BloodRequest, pk=pk, is_active=True)

        if blood_request.requester == request.user:
            return Response({"detail": "You cannot accept your own request."}, status=status.HTTP_400_BAD_REQUEST)

        if DonationHistory.objects.filter(donor=request.user, blood_request=blood_request).exists():
            return Response({"detail": "You have already accepted this request."}, status=status.HTTP_409_CONFLICT)

        DonationHistory.objects.create(donor=request.user, blood_request=blood_request)

        # Optionally mark request as inactive if fully accepted
        blood_request.is_active = False
        blood_request.status = 'accepted'
        blood_request.save()

        # Phase 1 communication: notify donor and requester via email
        try:
            requester_email = blood_request.requester.email
            donor_email = request.user.email
            subject = f"Hemogrid: Your blood request has been accepted (#{blood_request.id})"
            requester_msg = (
                f"Good news! Your request for {blood_request.blood_group} has been accepted.\n\n"
                f"Donor: {donor_email}\n"
                f"Location: {blood_request.location or 'N/A'}\n"
                f"Contact you provided: {blood_request.contact_info or 'N/A'}\n\n"
                f"Request details: {blood_request.details or 'N/A'}\n"
            )
            donor_msg = (
                f"You accepted a request (#{blood_request.id}) for {blood_request.blood_group}.\n\n"
                f"Recipient contact: {blood_request.contact_info or 'N/A'}\n"
                f"Location: {blood_request.location or 'N/A'}\n"
                f"Request details: {blood_request.details or 'N/A'}\n"
            )
            send_mail(subject, requester_msg, settings.DEFAULT_FROM_EMAIL, [requester_email], fail_silently=True)
            send_mail("Hemogrid: Request details", donor_msg, settings.DEFAULT_FROM_EMAIL, [donor_email], fail_silently=True)
        except Exception:
            pass

        return Response({"detail": "Request accepted successfully."}, status=status.HTTP_201_CREATED)


class RequestContactView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        br = get_object_or_404(BloodRequest, pk=pk)
        # Only requester or accepted donor may view contact
        is_participant = (br.requester == request.user) or DonationHistory.objects.filter(donor=request.user, blood_request=br).exists()
        if not is_participant:
            return Response({"detail": "Not permitted"}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "recipient_contact": br.contact_info,
            "recipient_email": br.requester.email,
            "location": br.location,
        })

class UpdateBloodRequestStatusView(generics.UpdateAPIView):
    serializer_class = BloodRequestStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BloodRequest.objects.all()

    def get_object(self):
        return get_object_or_404(BloodRequest, pk=self.kwargs['pk'], requester=self.request.user)


class CompleteBloodRequestView(generics.GenericAPIView):
    queryset = BloodRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        blood_request = get_object_or_404(BloodRequest, pk=pk)
        
        # Check if user is requester or donor
        is_requester = blood_request.requester == request.user
        is_donor = DonationHistory.objects.filter(donor=request.user, blood_request=blood_request).exists()
        
        if not (is_requester or is_donor):
            return Response({"detail": "You can only complete requests you're involved in."}, status=status.HTTP_403_FORBIDDEN)
        
        if blood_request.status != 'accepted':
            return Response({"detail": "Request must be accepted before completion."}, status=status.HTTP_400_BAD_REQUEST)
        
        blood_request.status = 'completed'
        blood_request.is_active = False
        blood_request.save()
        
        return Response({"detail": "Request completed successfully."}, status=status.HTTP_200_OK)


class CancelBloodRequestView(generics.GenericAPIView):
    queryset = BloodRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        blood_request = get_object_or_404(BloodRequest, pk=pk)
        
        # Check if user is requester or admin
        is_requester = blood_request.requester == request.user
        is_admin = request.user.is_staff or request.user.role == 'admin'
        
        if not (is_requester or is_admin):
            return Response({"detail": "You can only cancel your own requests."}, status=status.HTTP_403_FORBIDDEN)
        
        if blood_request.status in ['completed', 'cancelled']:
            return Response({"detail": "Request is already completed or cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        
        blood_request.status = 'cancelled'
        blood_request.is_active = False
        blood_request.save()
        
        return Response({"detail": "Request cancelled successfully."}, status=status.HTTP_200_OK)

class UserDonationHistoryView(generics.ListAPIView):
    serializer_class = DonationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return DonationHistory.objects.none()
        return DonationHistory.objects.filter(donor=self.request.user)

class MyRequestsView(generics.ListAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BloodRequest.objects.none()
        return BloodRequest.objects.filter(requester=self.request.user)

class DonationHistoryView(generics.ListAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BloodRequest.objects.none()
        return BloodRequest.objects.filter(donations__donor=self.request.user)

# -------------------------
# Admin Endpoints
# -------------------------
class AdminBloodRequestListView(generics.ListAPIView):
    queryset = BloodRequest.objects.all().order_by('-created_at')
    serializer_class = AdminBloodRequestSerializer
    permission_classes = [IsAdminUser]
    

class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        total_requests = BloodRequest.objects.count()
        fulfilled_requests = BloodRequest.objects.filter(status='completed').count()
        active_donors = DonationHistory.objects.values('donor').distinct().count()

        # Most active donors
        most_active_donors = User.objects.filter(donationhistory__isnull=False) \
            .annotate(donation_count=Count('donationhistory')) \
            .order_by('-donation_count')[:5] \
            .values('id', 'email', 'donation_count')

        stats = {
            'total_users': total_users,
            'total_requests': total_requests,
            'fulfilled_requests': fulfilled_requests,
            'active_donors': active_donors,
            'most_active_donors': list(most_active_donors),
        }
        return Response(stats)
