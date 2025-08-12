from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BloodRequest, DonationHistory
from .serializers import BloodRequestSerializer, DonationHistorySerializer

# Create your views here.

class BloodRequestCreateView(generics.CreateAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)


class BloodRequestListView(generics.ListAPIView):
    serializer_class = BloodRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BloodRequest.objects.filter(is_active=True).exclude(requester=self.request.user)


class AcceptBloodRequestView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        blood_request = get_object_or_404(BloodRequest, pk=pk, is_active=True)

        existing = DonationHistory.objects.filter(donor=request.user, blood_request=blood_request).first()
        if existing:
            return Response({"detail": "You have already accepted this request."}, status=status.HTTP_400_BAD_REQUEST)

        DonationHistory.objects.create(donor=request.user, blood_request=blood_request)
        return Response({"detail": "Request accepted successfully."}, status=status.HTTP_201_CREATED)


class UserDonationHistoryView(generics.ListAPIView):
    serializer_class = DonationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DonationHistory.objects.filter(donor=self.request.user)


