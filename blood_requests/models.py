from django.db import models
from django.conf import settings
from django.utils import timezone

class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requests_made'
    )
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    quantity = models.PositiveIntegerField(help_text="Units of blood required")
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Request by {self.requester.email} for {self.blood_group} ({self.quantity} units)"

    def mark_expired(self):
        """Check if the request has expired and deactivate it."""
        if self.expires_at and timezone.now() >= self.expires_at:
            self.is_active = False
            self.status = 'cancelled'
            self.save()

    def update_status(self, new_status):
        """Update the status of the request."""
        if new_status in dict(self.STATUS_CHOICES).keys():
            self.status = new_status
            if new_status in ['completed', 'cancelled']:
                self.is_active = False
            self.save()


class DonationHistory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    accepted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')

    def __str__(self):
        return f"{self.donor.email} donation for request {self.blood_request.id} ({self.status})"
