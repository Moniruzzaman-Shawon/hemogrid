from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_email = serializers.ReadOnlyField(source='recipient.email')
    blood_request_detail = serializers.ReadOnlyField(source='blood_request.id')

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['recipient', 'blood_request', 'created_at']
