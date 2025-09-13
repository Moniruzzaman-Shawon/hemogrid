from rest_framework import serializers
from .models import BloodRequest, DonationHistory
from django.utils import timezone
from accounts.models import User


# -------------------------
# Blood Request Serializer
# -------------------------
class BloodRequestSerializer(serializers.ModelSerializer):
    requester_email = serializers.ReadOnlyField(source='requester.email')
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = BloodRequest
        fields = '__all__'
        read_only_fields = ['requester', 'created_at', 'is_active']

    def get_is_expired(self, obj):
        return obj.expires_at and obj.expires_at < timezone.now()
# -------------------------
# Blood Request Status Update Serializer
# -------------------------
class BloodRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(BloodRequest.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status.")
        return value

# -------------------------
# Donation History Serializer
# -------------------------
class DonationHistorySerializer(serializers.ModelSerializer):
    donor_email = serializers.ReadOnlyField(source='donor.email')
    blood_request_detail = BloodRequestSerializer(source='blood_request', read_only=True)

    class Meta:
        model = DonationHistory
        fields = '__all__'
        read_only_fields = ['donor', 'accepted_at']

# -------------------------
# Admin view of blood requests
# -------------------------
class AdminBloodRequestSerializer(serializers.ModelSerializer):
    requester_email = serializers.ReadOnlyField(source='requester.email')

    class Meta:
        model = BloodRequest
        fields = '__all__'

# -------------------------
# For stats
# -------------------------
class AdminStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    fulfilled_requests = serializers.IntegerField()
    active_donors = serializers.IntegerField()



class AcceptBloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        # Minimal fields; the Accept view does not use serializer input
        fields = ['id', 'status']
        read_only_fields = ['id', 'status']
