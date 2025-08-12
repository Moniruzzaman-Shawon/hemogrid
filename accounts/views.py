from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from .serializers import RegisterSerializer, DonorProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from blood_requests.models import BloodRequest, DonationHistory
from blood_requests.serializers import BloodRequestSerializer, DonationHistorySerializer



# Create your views here.

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class VerifyEmailView(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


class DonorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DonorProfileSerializer
    permission_classes = []

    def get_object(self):
        return self.request.user
    

class DonorListView(generics.ListAPIView):
    serializer_class = DonorProfileSerializer
    permission_classes = [permissions.AllowAny]  # public access

    def get_queryset(self):
        # Return only users who are available donors
        return User.objects.filter(availability_status=True).exclude(full_name__isnull=True)
    

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all active requests excluding the user's own
        requests = BloodRequest.objects.filter(is_active=True).exclude(requester=request.user)
        requests_data = BloodRequestSerializer(requests, many=True).data

        # Get donation history of current user
        history = DonationHistory.objects.filter(donor=request.user)
        history_data = DonationHistorySerializer(history, many=True).data

        return Response({
            "recipient_requests": requests_data,
            "donation_history": history_data,
        })
    
class PublicDonorListView(generics.ListAPIView):
    queryset = User.objects.filter(availability_status=True).exclude(full_name__isnull=True)
    serializer_class = DonorProfileSerializer
    permission_classes = [permissions.AllowAny]