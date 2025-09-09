from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

# List user's notifications
class UserNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

# Mark notification as read
class MarkNotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()  # Add this line

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.all()

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification()
        return Notification.objects.get(pk=self.kwargs['pk'], recipient=self.request.user)

    def patch(self, request, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return Response({"detail": "Fake view for Swagger"}, status=200)
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"detail": "Notification marked as read"}, status=status.HTTP_200_OK)

