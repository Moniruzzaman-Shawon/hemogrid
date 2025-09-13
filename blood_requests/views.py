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
            user.availability_status = True  # optional: mark as available
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

        return Response({"detail": "Request accepted successfully."}, status=status.HTTP_201_CREATED)

class UpdateBloodRequestStatusView(generics.UpdateAPIView):
    serializer_class = BloodRequestStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BloodRequest.objects.all()

    def get_object(self):
        return get_object_or_404(BloodRequest, pk=self.kwargs['pk'], requester=self.request.user)

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
