from rest_framework import serializers
from .models import BloodRequest, DonationHistory

class BloodRequestSerializer(serializers.ModelSerializer):
    requester_email = serializers.ReadOnlyField(source='requester.email')

    class Meta:
        model = BloodRequest
        fields = '__all__'
        read_only_fields = ['requester', 'created_at', 'is_active']

class DonationHistorySerializer(serializers.ModelSerializer):
    donor_email = serializers.ReadOnlyField(source='donor.email')
    blood_request_detail = BloodRequestSerializer(source='blood_request', read_only=True)

    class Meta:
        model = DonationHistory
        fields = '__all__'
        read_only_fields = ['donor', 'accepted_at']
