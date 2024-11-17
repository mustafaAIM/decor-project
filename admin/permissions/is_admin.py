#permission
from rest_framework.permissions import BasePermission
#Role
from authentication.models.user_model import User

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.ADMIN