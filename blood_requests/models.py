from django.db import models
from django.conf import settings

# Create your models here.

class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests_made')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    quantity = models.PositiveIntegerField(help_text="Units of blood required")
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Request still open

    def __str__(self):
        return f"Request by {self.requester.email} for {self.blood_group} ({self.quantity} units)"


class DonationHistory(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]

    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='donations')
    accepted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')

    def __str__(self):
        return f"{self.donor.email} donation for request {self.blood_request.id} ({self.status})"
