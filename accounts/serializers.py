from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        email = validated_data['email'].lower()  # Normalize email case
        user = User.objects.create(
            email=email,
        )
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_link = f"http://localhost:8000/api/verify-email/{uid}/{token}/"

        send_mail(
            'Verify your Hemogrid account',
            f'Click here to verify: {verify_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return user


class DonorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'full_name',
            'age',
            'address',
            'last_donation_date',
            'availability_status'
        )
