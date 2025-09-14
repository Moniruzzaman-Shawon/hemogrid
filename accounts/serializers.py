from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import User 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
User = get_user_model()


# -------------------------
# Custom JWT Token Serializer
# -------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Check if user is verified
        if not self.user.is_verified:
            raise serializers.ValidationError({
                'detail': 'Please verify your email before logging in. Check your inbox for the verification link.',
                'email': self.user.email,
                'resend_verification': True
            })
        
        # Add custom fields to the response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role,
            'is_verified': self.user.is_verified,
            'is_staff': self.user.is_staff,
            'blood_group': self.user.blood_group,
            'availability_status': self.user.availability_status,
        }
        
        return data


# -------------------------
# Resend Verification Serializer
# -------------------------
class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value.lower())
            if user.is_verified:
                raise serializers.ValidationError("Email is already verified.")
            return value.lower()
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")


# Admin view of users
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'blood_group', 'is_active', 'is_verified', 'is_staff']
        read_only_fields = ['id', 'email']

# Admin update (suspend/verify)
class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active', 'is_verified']

# -------------------------
# Register Serializer
# -------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    full_name = serializers.CharField(required=True)
    age = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'age')

    def create(self, validated_data):
        email = validated_data['email'].lower()
        password = validated_data.pop('password')
        full_name = validated_data.pop('full_name')
        age = validated_data.pop('age')

        user = User.objects.create(
            email=email,
            full_name=full_name,
            age=age,
            is_active=False,  # must verify email
            is_verified=False,
        )
        user.set_password(password)
        user.save()
        # Email sending is handled in the view to avoid duplication
        return user


# -------------------------
# Donor Profile Serializer
# -------------------------
class DonorProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'age', 'address',
            'last_donation_date', 'availability_status', 'blood_group',
            'is_verified', 'profile_picture', 'role',
        ]
# -------------------------
# Update Availability Serializer
# -------------------------
class AvailabilitySerializer(serializers.Serializer):
    availability_status = serializers.ChoiceField(choices=[('available','Available'),('not_available','Not Available'),('busy','Busy')])

# -------------------------
# Verify Donor Serializer
# -------------------------
class VerifyDonorSerializer(serializers.Serializer):
    is_verified = serializers.BooleanField()

# -------------------------
# Forgot Password
# -------------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

# -------------------------
# Reset Password
# -------------------------
class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return attrs

# -------------------------
# Change Password
# -------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from the old password."})
        return attrs

# -------------------------
# Update Email
# -------------------------
class UpdateEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
    
# -------------------------
# Availability
# -------------------------
class AvailabilitySerializer(serializers.Serializer):
    availability_status = serializers.ChoiceField(
        choices=[
            ('available', 'Available'),
            ('not_available', 'Not Available'),
            ('busy', 'Busy')
        ]
    )




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # important for email login

    def validate(self, attrs):
        # Normalize and pre-check user state for clearer errors
        email = attrs.get(self.username_field)
        if isinstance(email, str):
            # Resolve actual stored email case via iexact lookup
            existing = get_user_model().objects.filter(email__iexact=email).first()
            if existing:
                # Early error for inactive/unverified accounts
                if not existing.is_active or not getattr(existing, 'is_verified', True):
                    raise serializers.ValidationError({
                        "detail": "Please verify your email before logging in.",
                        "code": "inactive_or_unverified",
                    })
                # Use stored casing to satisfy authenticators that compare strictly
                attrs[self.username_field] = existing.email

        data = super().validate(attrs)

        # After successful credential validation, attach user info
        user = self.user  # set by TokenObtainPairSerializer

        # Add extra info to response if needed
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'role': getattr(user, 'role', None),
            'is_verified': getattr(user, 'is_verified', False),
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add extra claims if you want
        token['email'] = user.email
        token['role'] = user.role
        return token

# -------------------------
# Resend Verification
# -------------------------
class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
