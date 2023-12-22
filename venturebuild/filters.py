from rest_framework import filters
from django.db.models import Q

from organizations.models import Organization
from django.contrib.auth import get_user_model
User = get_user_model()

'''
File contains custom filters used across the whole backend API
'''

# Returns only approved items if user is not an admin
class FilterOrgsToUser(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user

        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Organization.objects.none()

        return queryset if user.is_staff else queryset.filter(id__in=[org.id for org in list(user.organizations.all())])

# Returns only approved items if user is not an admin
class AdminOrApprovedFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset
        return queryset.filter(approved=True)

# Returns only approved items if user is not approved
class AdminOrParentApprovedFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset
        return queryset.filter(parent__approved=True)

# Filters queryset to set containing users id (admin can see all)
# Useful for accounts backend
class AdminOrSelfFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not request.user: return queryset.none()
        if request.user.is_staff: return queryset
        return queryset.filter(id=request.user.id)

# Filters queryset to set containing users id (superuser can see all)
# Useful for accounts backend
class SuperuserOrSelfFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not request.user: return queryset.none()
        if request.user.is_admin: return queryset
        return queryset.filter(id=request.user.id)

# Filters queryset to thaat containing users id
# Useful for favourites and ratings (will not let admin see others favourites and ratings)
class UserFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)
