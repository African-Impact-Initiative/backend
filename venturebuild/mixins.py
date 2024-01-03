from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsAdminUserOrReadOnly, IsStaffUser, IsOwner, IsOwnerOrReadOnly
from .filters import FilterOrgsToUser, AdminOrSelfFilterBackend, AdminOrParentApprovedFilterBackend, SuperuserOrSelfFilterBackend, UserFilterBackend

'''
File contains mixins used across the whole API
'''

# Give this mixin to verify users are logged in
class UserMixin():
    permission_classes = [IsAuthenticatedOrReadOnly]

# Give this mixin to allow anyone
class AllowAll():
    permission_classes = []

# Give this mixin to resources and it will show users resources but they will not be able to modify them
# Admin will be able to modify all resources
class GetOrAdminMixin():
    permission_classes = [IsAdminUserOrReadOnly]

class StaffOnlyMixin():
    permission_classes = [IsStaffUser]

# Give this mixin to only allow access to owner
class OwnerOnlyMixin():
    permission_classes = [IsOwner]

# Give this mixin to only modification to owner
class OwnerOrReadOnlyMixin():
    permission_classes = [IsOwnerOrReadOnly]

# Give this mixin to resources and it will show users approved resources
# Admin will see all resources
class PublicResourceMixin():
    filter_backends = [FilterOrgsToUser]

# Give this mixin and users will only be able to see objects that contain their userid
# Admin will see all
class AdminOrSelfMixin():
    filter_backends = [AdminOrSelfFilterBackend]

# Give this mixin and users will only be able to see objects that contain their userid
# Superuser will see all
class SuperuserOrSelfMixin():
    filter_backends = [SuperuserOrSelfFilterBackend]

# Give this mixin and it will filter resources based on whether parent is approved or not
# Admin see all
class ParentApprovedMixin():
    filter_backends = [AdminOrParentApprovedFilterBackend]

# Give this mixin to filter querset to objects only containing users id
class UserFilterMixin():
    filter_backends = [UserFilterBackend]