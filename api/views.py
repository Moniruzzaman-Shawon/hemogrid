from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_home(request):
    return Response({
        "Authentication": {
            "Register": "/api/register/",
            "Login": "/api/login/",
            "Refresh Token": "/api/jwt/refresh/",
        },
        "Blood Requests": {
            "List Requests": "/api/requests/",
            "Create Request": "/api/blood-requests/create/",
            "Accept Request": "/api/blood-requests/<id>/accept/",
        },
        "Users": {
            "List Users": "/api/donors/",
            "User Profile": "/api/donor-profile/",
        }
    })
