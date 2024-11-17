from rest_framework.permissions import BasePermission
from authentication.models import User
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.is_anonymous:
            return False
        return request.user.role == User.Role.ADMIN