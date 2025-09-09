# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class APIHomeView(APIView):
    permission_classes = [AllowAny]  # Everyone can see this endpoint

    def get(self, request):
        data = {
            "Authentication": {
                "Register": "/api/auth/register/",
                "Login": "/api/auth/jwt/create/",
                "Refresh Token": "/api/auth/jwt/refresh/"
            },
            "Blood Requests": {
                "List Requests": "/api/requests/",
                "Create Request": "/api/blood-requests/create/",
                "Accept Request": "/api/blood-requests/<id>/accept/",
                "My Requests": "/api/my-requests/",
                "Update Status": "/api/blood-requests/<id>/update-status/"
            },
            "Donations": {
                "Donation History": "/api/donation-history/",
                "All Donation History": "/api/donation-history/all/"
            },
            "Users": {
                "List Users": "/api/donors/",
                "User Profile": "/api/donor-profile/"
            },
            "Admin": {
                "List All Users": "/api/admin/users/",
                "List All Requests": "/api/admin/requests/",
                "Stats": "/api/admin/stats/"
            },
            "Notifications": {
                "List": "/api/notifications/",
                "Mark Read": "/api/notifications/mark-read/<id>/"
            }
        }
        return Response(data)
