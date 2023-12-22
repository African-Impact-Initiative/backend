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