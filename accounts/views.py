from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
import os

from .serializers import ChangeEmailSerializer, UserSerializer, GetUserSerializer, ChangePasswordSerializer, UpdatePersonalInfo, AddOrganization, TermsOfUseAgreement
# from .tokens import account_activation_token
from venturebuild.mixins import UserMixin, SuperuserOrSelfMixin, AllowAll, StaffOnlyMixin

from organizations.models import Organization

# from venturebuild.email_server import promote, demote, change_password, account_deleted, change_email, welcome_email

from django.contrib.auth import get_user_model
User = get_user_model()

# User general REST endpoint GET, POST
class UserListCreateAPIView(AllowAll, UserMixin, generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = GetUserSerializer # Default class is the GET class

    def perform_create(self, serializer):
        user = None

        # If the user is superuser and they want to creat superuser
        if not self.request.user.is_anonymous and self.request.user.is_admin and serializer.data.get('admin', False):
            user = User.objects.create_superuser(
                password=serializer.data['password'],
                email=serializer.data['email'],
                first_name=serializer.data['first_name'],
                last_name=serializer.data['last_name']
            )
        # If the user is superuser and want to create a staff
        elif not self.request.user.is_anonymous and self.request.user.is_admin and serializer.data.get('staff', False):
            user = User.objects.create_staffuser(
                password=serializer.data['password'],
                email=serializer.data['email'],
                first_name=serializer.data['first_name'],
                last_name=serializer.data['last_name']
            )
        # Regular user
        else:
            user = User.objects.create_user(
                password=serializer.data['password'],
                email=serializer.data['email'],
                first_name=serializer.data['first_name'],
                last_name=serializer.data['last_name']
            )

        # account activation token
        # token = account_activation_token.make_token(user)
        # welcome_email(user, f"{os.environ.get('FRONTEND_URL')}/activate/?id={user.id}&token={token}")

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)

        if res.status_code == status.HTTP_200_OK or res.status_code == status.HTTP_201_CREATED:
            return Response(status=status.HTTP_201_CREATED, data={'message': 'User created successfully'})
        return res

    # make sure that POST is only done on the UserSerializer NEVER allow on GET serializer (can modify staff and admin)
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSerializer
        return GetUserSerializer

# User REST /:id endpoint GET, PUT, DELETE
class UserViewUpdateDeleteAPIView(UserMixin, SuperuserOrSelfMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = GetUserSerializer

    # update a user
    def perform_update(self, serializer):
        obj = self.get_object()

        # if the user is admin trying to modify other user (note need admin, staff will not work here)
        if self.request.user.is_admin and self.request.user.id != obj.id:
            # check what they were promoted to
            # sent = False
            staff = serializer.validated_data.get('staff', False)
            admin = serializer.validated_data.get('admin', False)

            # # if admin status changed
            # if admin != obj.admin:
            #     sent = True
            #     if admin:
            #         promote(obj)
            #     else:
            #         demote(obj)

            # # if staff status changed
            # if staff != obj.staff and not sent:
            #     if staff:
            #         promote(obj)
            #     else:
            #         demote(obj)

            # do not allow the admin to modify anything other that staff/admin status
            serializer.save(
                staff=staff,
                admin=admin,
                email=obj.email,
                is_active=obj.is_active,
                first_name=obj.first_name,
                last_name=obj.last_name
            )
        # if user trying to update self do regular stuff
        else:
            return super().perform_update(serializer)

    # when destroy
    def perform_destroy(self, instance):
        obj = self.get_object()

        if self.request.user.id == obj.id:
            # send email
            # account_deleted(obj)
            return super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        # verify password is correct (on frontend user enters password to verify they are themself)
        # only for users which have a password (Google users will just confirm if they are sure)
        if obj.has_usable_password() and not obj.check_password(request.data.get("password")):
            return Response({"password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        if self.request.user.is_admin and self.request.user.id != obj.id:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'You cannot delete a user other than yourself'})
        return super().destroy(request, *args, **kwargs)

    # Only allow PUT to the user serializer
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UserSerializer
        return GetUserSerializer

# on frontend it is tricky to find out who is logged in since admin can see multiple users (needed to promote/demote and site analytics)
# to resolve this create /me endpoint which returns users associated with the token
class GetUser(UserMixin, generics.RetrieveAPIView):
    def get_object(self):
        obj = self.request.user
        return obj

    def get_serializer_class(self):
        return GetUserSerializer

# returns all admins
class GetAdmins(StaffOnlyMixin, generics.ListAPIView):
    def get_queryset(self):
        return User.objects.filter(staff=True)

    def get_serializer_class(self):
        return GetUserSerializer

# used to change password
class ChangePasswordView(UserMixin, generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User

    # make sure that the only user you can access is yourself
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if self.object.password != None and not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            # build this response since django will otherwise return the user (also contains UNHASHED password, very bad :( )
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            # send email
            # change_password(self.object)

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangeEmailView(UserMixin, generics.UpdateAPIView):
    serializer_class = ChangeEmailSerializer
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("password")):
                return Response({"password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            try:
                u = User.objects.get(email=serializer.data.get("email"))
            except User.DoesNotExist:
                user = User.objects.get(id=self.object.id)
                user.email = serializer.data.get("email")
                user.save()

                # build this response since django will otherwise return the user (also contains UNHASHED password, very bad again! :( )
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Email updated successfully',
                    'data': []
                }

                # send email
                # change_email(user)

                return Response(response)

            # if email in use return this
            return Response({"email": "email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


####################### Onboarding #######################

class PersonInfoUpdate(UserMixin, generics.UpdateAPIView):
    serializer_class = UpdatePersonalInfo
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(id=self.object.id)

        if serializer.is_valid():
            if not user.terms_of_use:
                # build this response
                response = {
                    'status': 'error',
                    'code': status.HTTP_403_FORBIDDEN,
                    'message': 'Must agree to Terms of Use before proceeding',
                    'data': []
                }

                return Response(response)

            user.first_name = serializer.data.get("first_name")
            user.last_name = serializer.data.get("last_name")
            user.role = serializer.data.get("role")

            if request.FILES.get("photo", False):
                user.photo = request.FILES.get("photo")

            if serializer.data.get("linkedin", False):
                user.linkedin = serializer.data.get("linkedin")

            if serializer.data.get("country", False):
                user.country = serializer.data.get("country")

            if serializer.data.get("bio", False):
                user.bio = serializer.data.get("bio")

            user.save()

            # build this response
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Personal information updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TermsOfUseUpdate(UserMixin, generics.UpdateAPIView):
    serializer_class = TermsOfUseAgreement
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        user = User.objects.get(id=self.object.id)

        if serializer.is_valid():
            if serializer.data.get("terms", False):
                user.terms_of_use = True
                user.save()

                # build this response
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Terms agreed',
                    'data': []
                }
            else:
                # build this response
                response = {
                    'status': 'error',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Terms not agreed',
                    'data': []
                }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddOrganizationToUser(UserMixin, generics.UpdateAPIView):
    serializer_class = AddOrganization
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.get(id=self.object.id)

            try:
                o = Organization.objects.get(id=serializer.data.get("org"))
            except Organization.DoesNotExist:
                # build this response
                response = {
                    'status': 'error',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Organization not found',
                    'data': []
                }

                return Response(response)

            user.organizations.add(o)
            user.save()

            response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Organization added',
                    'data': []
                }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# for some reason need csrf exempt for the function idk why though CORS should have handled this
# @csrf_exempt
# def activate(request, uidb64, token):
#     # get user
#     try:
#         user = User.objects.get(pk=uidb64)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     # verify user and token matches
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True   # account is now active
#         user.is_verified = True   # account is now active
#         user.save()

#         res = HttpResponse()
#         res.status_code = 200

#         return res
#     else:
#         res = HttpResponse()
#         res.status_code = 400
#         return res