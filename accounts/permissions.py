from rest_framework import permissions

class IsRole(permissions.BasePermission):
    """
    Custom permission to allow access only to users with specific role(s).
    Usage:
        permission_classes = [IsRole.with_roles('admin')]
        permission_classes = [IsRole.with_roles('donor', 'requester')]
    """

    def __init__(self, roles=None):
        self.roles = roles or []

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in self.roles
        )

    @classmethod
    def with_roles(cls, *roles):
        """
        Factory method so we can do:
        permission_classes = [IsRole.with_roles('admin')]
        """
        return type("IsRoleSubclass", (cls,), {"__init__": lambda self: super(cls, self).__init__(roles)})
