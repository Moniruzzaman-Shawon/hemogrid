from rest_framework import permissions

class IsRole(permissions.BasePermission):
    """
    Custom permission to allow access only to users with specific role(s).
    Usage: permission_classes = [IsRole('donor')] or IsRole('admin', 'requester')
    """
    def __init__(self, *roles):
        self.roles = roles

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in self.roles
        )
