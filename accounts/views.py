from rest_framework import generics, status, filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .serializers import (
    RegisterSerializer,
    DonorProfileSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    UpdateEmailSerializer,
    AvailabilitySerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    MyTokenObtainPairSerializer
)
from blood_requests.models import BloodRequest, DonationHistory
from blood_requests.serializers import BloodRequestSerializer, DonationHistorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

User = get_user_model()


def build_verification_link(request, uid, token):
    """
    Determine the verification link to send to the user.
    Preference order:
      1. EMAIL_VERIFICATION_BASE_URL (explicit override)
      2. FRONTEND_URL (for SPA-driven flows)
      3. Current request domain pointing to the API endpoint
    """
    base_url = getattr(settings, 'EMAIL_VERIFICATION_BASE_URL', None)
    if base_url:
        return f"{base_url.rstrip('/')}/verify-email/{uid}/{token}/"

    frontend_base = getattr(settings, 'FRONTEND_URL', None)
    if frontend_base:
        return f"{str(frontend_base).rstrip('/')}/verify-email/{uid}/{token}/"

    verify_path = reverse('auth:verify-email', kwargs={'uidb64': uid, 'token': token})
    if request:
        return request.build_absolute_uri(verify_path)
    return verify_path

# -------------------------
# Only admins allowed
# -------------------------
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

# -------------------------
# Admin User Views
# -------------------------
class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]

class AdminUserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [IsAdminUser]

# -------------------------
# Registration & Email Verification
# -------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Create user inactive
        user = serializer.save(is_active=False, is_verified=False)
        # Generate token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        # Send verification email using configured link base
        verify_link = build_verification_link(self.request, uid, token)
        send_mail(
            "Verify your Hemogrid account",
            f"Click the link to verify your account: {verify_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

from rest_framework.views import APIView

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# Resend Verification Email
# -------------------------
from .serializers import ResendVerificationSerializer

class ResendVerificationView(generics.GenericAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()

        # Use generic response to avoid email enumeration
        message = "If the email is registered and unverified, a verification link has been sent."

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"message": message}, status=status.HTTP_200_OK)

        if user.is_active and getattr(user, 'is_verified', False):
            return Response({"message": message}, status=status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_link = build_verification_link(self.request, uid, token)
        send_mail(
            'Verify your Hemogrid account',
            f'Click here to verify your account: {verify_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({"message": message}, status=status.HTTP_200_OK)

# -------------------------
# Donor Profile & Listing
# -------------------------
class DonorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DonorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self):
        return self.request.user

class PublicDonorListView(generics.ListAPIView):
    queryset = User.objects.filter(role="donor", is_active=True, is_verified=True)
    serializer_class = DonorProfileSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    # Filters by blood group and availability
    filterset_fields = ['blood_group', 'availability_status']

    # Search by name or address
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
            # Send users to the frontend reset page where they can submit a new password
            frontend_base = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            reset_link = f"{frontend_base}/reset-password/{uid}/{token}/"
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
        self.object.is_verified = False
        self.object.save()

        # Send verification email
        uid = urlsafe_base64_encode(force_bytes(self.object.pk))
        token = default_token_generator.make_token(self.object)
        frontend_base = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        verify_link = f"{frontend_base}/verify-email/{uid}/{token}/"
        send_mail(
            'Verify your new Hemogrid email',
            f'Click here to verify your new email: {verify_link}',
            settings.DEFAULT_FROM_EMAIL,
            [self.object.email],
            fail_silently=False,
        )

        return Response({"message": "Email updated successfully. Please verify your new email."}, status=status.HTTP_200_OK)

# -------------------------
# Update Availability
# -------------------------
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



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
