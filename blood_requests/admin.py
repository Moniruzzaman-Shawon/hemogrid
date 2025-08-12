from django.contrib import admin
from .models import BloodRequest, DonationHistory

# Register your models here.

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requester', 'blood_group', 'quantity', 'location', 'contact_info', 'is_active', 'created_at')
    search_fields = ('requester__email', 'location', 'contact_info')
    list_filter = ('blood_group', 'is_active', 'created_at')
    ordering = ('-created_at',)


@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'donor', 'blood_request', 'status', 'accepted_at')  
    search_fields = ('donor__email', 'blood_request__location')
    list_filter = ('status', 'accepted_at')  
    ordering = ('-accepted_at',)  