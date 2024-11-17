from rest_framework.permissions import BasePermission
from authentication.models import User
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user.role == User.Role.ADMIN