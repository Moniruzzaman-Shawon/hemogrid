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
        )
        user.set_password(password)
        user.save()

        # Send verification email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_link = f"http://localhost:3000/verify-email/{uid}/{token}/"
        send_mail(
            'Verify your Hemogrid account',
            f'Click here to verify your account: {verify_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
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

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add extra claims if you want
        token['email'] = user.email
        token['role'] = user.role
        return token
