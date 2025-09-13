from rest_framework import permissions

class IsRole(permissions.BasePermission):
    """
    Custom permission to allow access only to users with specific role(s).
    Usage:
        permission_classes = [IsRole.with_roles('admin')]
        permission_classes = [IsRole.with_roles('donor', 'requester')]
    """

    def __init__(self, roles=None):
        # Support instance-specific roles when provided; otherwise use class attr
        if roles is not None:
            self.roles = list(roles)

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in self.roles
        )

    @classmethod
    def with_roles(cls, *roles):
        """
        Factory to create a permission class bound to specific roles, e.g.:
        permission_classes = [IsRole.with_roles('admin', 'staff')]
        """
        # Create a subclass with a class attribute 'roles'. DRF will instantiate
        # it without args, and instances will read roles from the class.
        return type("IsRoleSubclass", (cls,), {"roles": list(roles)})
