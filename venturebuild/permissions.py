from rest_framework import permissions

'''
File contains custom permissions used in backend API
'''

# Allows users to see info but only admin can modify it
class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.user.is_staff: return True
        return request.method in permissions.SAFE_METHODS

# Allows only staff
class IsStaffUser(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.user.is_staff: return True
        return False
    
# Allows only owner
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.owner
            and request.user.organization == obj
        )
    
# Owner or readonly
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.owner
            and request.user.organization == obj
        )