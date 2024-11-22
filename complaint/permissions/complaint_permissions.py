from rest_framework import permissions

class IsCustomerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Staff members to have full access
    - Customers to access only their own complaints
    - Proper method-based permissions
    """

    def has_permission(self, request, view):
        """
        Define general permission rules:
        - Must be authenticated
        - Staff can access everything
        - Customers can only use specific methods
        """
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        if hasattr(request.user, 'customer'):
            if view.action == 'statistics':
                return False
                
            if view.action in ['list', 'retrieve', 'create']:
                return True
                
            if view.action in ['update', 'partial_update', 'destroy']:
                return False  
                
            if view.action in ['resolve', 'reopen', 'escalate']:
                return True
                
        return False

    def has_object_permission(self, request, view, obj):
        """
        Define object-level permission rules:
        - Staff can access any object
        - Customers can only access their own complaints
        - Certain actions are restricted based on complaint status
        """
        if request.user.is_staff:
            return True

        if hasattr(request.user, 'customer'):
            if obj.customer != request.user.customer:
                return False

            if view.action in ['update', 'partial_update', 'destroy']:
                return obj.status == 'PENDING'

            if view.action == 'resolve':
                return obj.status in ['PENDING', 'IN_PROGRESS']
                
            if view.action == 'reopen':
                return obj.status in ['RESOLVED', 'CLOSED']
                
            if view.action == 'escalate':
                return obj.status != 'CLOSED'

            return True

        return False

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff members to edit complaints.
    Others can only read.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of a complaint or staff members
    to view/edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if hasattr(request.user, 'customer'):
            return obj.customer == request.user.customer

        return False

class CanModifyComplaint(permissions.BasePermission):
    """
    Custom permission to control who can modify complaints based on their status
    and the user's role.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(request.user, 'customer'):
            return (
                obj.customer == request.user.customer and 
                obj.status == 'PENDING'
            )

        return False
