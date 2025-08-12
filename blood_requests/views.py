from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from .models import BloodRequest, DonationHistory
from .serializers import BloodRequestSerializer, DonationHistorySerializer
from django_filters.rest_framework import DjangoFilterBackend



# Create a new blood request
class BloodRequestCreateView(generics.CreateAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


# List all active requests except the logged-in user's own requests
class BloodRequestListView(generics.ListAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    # Filtering by blood group
    filterset_fields = ['blood_group']
    # Search by location or description
    search_fields = ['location', 'details']
    # Sort by date
    ordering_fields = ['created_at']

    def get_queryset(self):
        return BloodRequest.objects.filter(is_active=True).exclude(requester=self.request.user)

# Accept a blood request
class AcceptBloodRequestView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        blood_request = get_object_or_404(BloodRequest, pk=pk, is_active=True)

        # Prevent accepting own request
        if blood_request.requester == request.user:
            return Response(
                {"detail": "You cannot accept your own request."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent duplicate acceptance
        existing = DonationHistory.objects.filter(
            donor=request.user, blood_request=blood_request
        ).first()
        if existing:
            return Response(
                {"detail": "You have already accepted this request."},
                status=status.HTTP_409_CONFLICT
            )

        # Record donation
        DonationHistory.objects.create(donor=request.user, blood_request=blood_request)

        # Optionally mark request as inactive after first acceptance
        blood_request.is_active = False
        blood_request.save()

        return Response(
            {"detail": "Request accepted successfully."},
            status=status.HTTP_201_CREATED
        )


# View logged-in user's donation history
class UserDonationHistoryView(generics.ListAPIView):
    serializer_class = DonationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DonationHistory.objects.filter(donor=self.request.user)


# Recipient's request list (My Requests)
class MyRequestsView(generics.ListAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BloodRequest.objects.filter(requester=self.request.user)


# Donor's donation history (via BloodRequest relation)
class DonationHistoryView(generics.ListAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BloodRequest.objects.filter(
            donations__donor=self.request.user
        )