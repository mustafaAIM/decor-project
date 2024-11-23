from rest_framework import permissions
from authentication.models import User
class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == User.Role.ADMIN)

class IsCustomerAndCreateOnly(permissions.BasePermission):
    """
    Permission to only allow customers to create complaints.
    They can also view their own complaints but cannot modify them.
    """
    def has_permission(self, request, view):
        if not request.user.role == User.Role.ADMIN:
            if view.action in ['create', 'list', 'retrieve']:
                return True
            return False
        return False

    def has_object_permission(self, request, view, obj):
        return obj.customer.user == request.user

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of a complaint or admins to view it.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        return obj.customer.user == request.user and view.action in ['retrieve']
