from rest_framework import generics, permissions
from accounts.models import User
from blood_requests.models import BloodRequest, DonationHistory
from .serializers import AdminUserSerializer, AdminBloodRequestSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count


# -----------------
# User Management
# -----------------
class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminUserSuspendView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_active = False
            user.save()
            return Response({"status": "suspended"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class AdminUserVerifyView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_verified = True
            user.save()
            return Response({"status": "verified"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


# -----------------
# Blood Requests
# -----------------
class AdminBloodRequestListView(generics.ListAPIView):
    queryset = BloodRequest.objects.all()
    serializer_class = AdminBloodRequestSerializer
    permission_classes = [permissions.IsAdminUser]


# -----------------
# Statistics
# -----------------
class AdminStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_verified_donors = User.objects.filter(is_verified=True, role="donor").count()
        total_requests = BloodRequest.objects.count()
        completed_requests = BloodRequest.objects.filter(status="completed").count()
        fulfillment_rate = (
            (completed_requests / total_requests) * 100 if total_requests > 0 else 0
        )

        active_donors = (
            DonationHistory.objects.values("donor")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )

        return Response({
            "total_users": total_users,
            "verified_donors": total_verified_donors,
            "total_requests": total_requests,
            "completed_requests": completed_requests,
            "fulfillment_rate": fulfillment_rate,
            "most_active_donors": list(active_donors),
        })
