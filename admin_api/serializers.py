from rest_framework import serializers
from accounts.models import User
from blood_requests.models import BloodRequest, DonationHistory


# -----------------
# User Serializer
# -----------------
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_verified', 'blood_group']


# -----------------
# Blood Request Serializer
# -----------------
class AdminBloodRequestSerializer(serializers.ModelSerializer):
    requester_email = serializers.ReadOnlyField(source='requester.email')

    class Meta:
        model = BloodRequest
        fields = '__all__'
