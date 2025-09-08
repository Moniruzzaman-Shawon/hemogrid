from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    RegisterSerializer,
    DonorProfileSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    UpdateEmailSerializer,
    AvailabilitySerializer
)
from blood_requests.models import BloodRequest, DonationHistory
from blood_requests.serializers import BloodRequestSerializer, DonationHistorySerializer
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()

# -------------------------
# Registration & Email Verification
# -------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]

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
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# Donor Profile & Listing
# -------------------------
class DonorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DonorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class DonorListView(generics.ListAPIView):
    serializer_class = DonorProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = User.objects.filter(availability_status=True).exclude(full_name__isnull=True)
        blood_group = self.request.query_params.get('blood_group')
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        return queryset

class PublicDonorListView(generics.ListAPIView):
    queryset = User.objects.filter(availability_status=True).exclude(full_name__isnull=True)
    serializer_class = DonorProfileSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['blood_group']
    search_fields = ['full_name', 'address']

# -------------------------
# Dashboard
# -------------------------
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = BloodRequest.objects.filter(is_active=True).exclude(requester=request.user)
        requests_data = BloodRequestSerializer(requests, many=True).data
        history = DonationHistory.objects.filter(donor=request.user)
        history_data = DonationHistorySerializer(history, many=True).data
        return Response({
            "recipient_requests": requests_data,
            "donation_history": history_data,
        })

# -------------------------
# Password Management
# -------------------------
class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:8000/api/reset-password/{uid}/{token}/"
            send_mail(
                'Reset your Hemogrid password',
                f'Click here to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass
        return Response({"message": "Password reset link sent if email exists"}, status=status.HTTP_200_OK)

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not self.object.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        self.object.set_password(serializer.validated_data['new_password'])
        self.object.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)


# -------------------------
# Update Email
# -------------------------
class UpdateEmailView(generics.UpdateAPIView):
    serializer_class = UpdateEmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.object.email = serializer.validated_data['new_email'].lower()
        self.object.is_verified = False  # Require re-verification for new email
        self.object.save()

        # Send verification email
        uid = urlsafe_base64_encode(force_bytes(self.object.pk))
        token = default_token_generator.make_token(self.object)
        verify_link = f"http://localhost:8000/api/verify-email/{uid}/{token}/"
        send_mail(
            'Verify your new Hemogrid email',
            f'Click here to verify your new email: {verify_link}',
            settings.DEFAULT_FROM_EMAIL,
            [self.object.email],
            fail_silently=False,
        )

        return Response({"message": "Email updated successfully. Please verify your new email."}, status=status.HTTP_200_OK)



class UpdateAvailabilityView(generics.UpdateAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.object.availability_status = serializer.validated_data['availability_status']
        self.object.save()
        return Response({"message": f"Availability updated to {self.object.availability_status}"}, status=status.HTTP_200_OK)
