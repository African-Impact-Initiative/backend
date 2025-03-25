from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Invitation
from .serializers import InvitationSerializer
from venturebuild.email_server import send_invitation_email
from venturebuild import settings
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from django.utils.crypto import get_random_string
from django.contrib.auth import login as login
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from social_django.utils import load_strategy
from social_django.utils import load_backend
from social_core.exceptions import MissingBackend, AuthException

import json
import os

from .serializers import ChangeEmailSerializer, UserSerializer, GetUserSerializer, ChangePasswordSerializer, \
    UpdatePersonalInfo, AddOrganization, TermsOfUseAgreement, ForgotPasswordSerializer
from .serializers import ChangeEmailSerializer, UserSerializer, GetUserSerializer, ChangePasswordSerializer, UpdatePersonalInfo, AddOrganization, TermsOfUseAgreement, UpdateTeamStatusSerializer, ForgotPasswordSerializer
from .tokens import account_activation_token
from venturebuild.mixins import UserMixin, SuperuserOrSelfMixin, AllowAll, StaffOnlyMixin
from organizations.models import Organization

from venturebuild.email_server import promote, demote, change_password, account_deleted, change_email, welcome_email, \
    forgot_password

from venturebuild.email_server import promote, demote, change_password, account_deleted, change_email, welcome_email, forgot_password
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


# User general REST endpoint GET, POST
class UserListCreateAPIView(AllowAll, UserMixin, generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = GetUserSerializer  # Default class is the GET class

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
        token = account_activation_token.make_token(user)
        # welcome_email(user, f"{os.environ.get('FRONTEND_URL')}/activate/?id={user.id}&token={token}")
        # Need to edit the frontend link such that it is dynamic and
        # reflects the actual frontend url. The current link has been hardcoded just as a placeholder and for testing
        # purposes
        welcome_email(user, f"http://localhost:8000/api/accounts/activate/?id={user.id}&token={token}")

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

            # if admin status changed
            if admin != obj.admin:
                sent = True
                if admin:
                    promote(obj)
                else:
                    demote(obj)

            # if staff status changed
            if staff != obj.staff and not sent:
                if staff:
                    promote(obj)
                else:
                    demote(obj)

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
            account_deleted(obj)
            return super().perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        # verify password is correct (on frontend user enters password to verify they are themself)
        # only for users which have a password (Google users will just confirm if they are sure)
        if obj.has_usable_password() and not obj.check_password(request.data.get("password")):
            return Response({"password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        if self.request.user.is_admin and self.request.user.id != obj.id:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data={'error': 'You cannot delete a user other than yourself'})
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
            change_password(self.object)

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
                change_email(user)

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
        print(serializer)
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

            # Add team_status update
            if serializer.data.get("team_status"):
                user.team_status = serializer.data.get("team_status")
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

            user.organization = o
            user.save()

            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Organization added',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Add new view for updating team status
class UpdateTeamStatus(UserMixin, generics.UpdateAPIView):
    serializer_class = UpdateTeamStatusSerializer
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = User.objects.get(id=self.object.id)
            user.team_status = serializer.data.get("team_status")
            user.save()

            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Team status updated successfully',
                'data': {
                    'team_status': user.team_status
                }
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def create(self, request, *args, **kwargs):
        # Get the organization
        organization_id = request.data.get('organization')
        organization = get_object_or_404(Organization, id=organization_id)
        
        # Check if user has permission to invite (must be owner or co-owner)
        if not (request.user.owner and request.user.organization.id == organization_id) and \
           not (request.user.coowner == organization_id):
            return Response(
                {"error": "You don't have permission to invite members to this organization"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if there's a pending invitation for this email
        email = request.data.get('email')
        if Invitation.objects.filter(email=email, organization=organization, status='pending').exists():
            return Response(
                {"error": "A pending invitation already exists for this email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is already a member of the organization
        User = get_user_model()
        if User.objects.filter(email=email, organization=organization).exists():
            return Response(
                {"error": "This user is already a member of your organization"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique token
        token = get_random_string(64)
        
        # Create invitation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save(invited_by=request.user, token=token)

        # Generate invitation link
        invitation_link = f"{settings.FRONTEND_URL}/join-organization/{token}"
        # Send invitation email
        try:
            send_invitation_email(
                invitation.email,
                organization.name,
                invitation_link
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            invitation.delete()
            return Response(
                {"error": f"Failed to send invitation email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {"error": "This invitation has already been processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update invitation status
        invitation.status = 'accepted'
        invitation.save()

        # Update user's organization
        request.user.organization = invitation.organization
        request.user.save()
        invitation.delete()

        return Response({"message": "Invitation accepted successfully"})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {"error": "This invitation has already been processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invitation.status = 'declined'
        invitation.save()
        invitation.delete()

        return Response({"message": "Invitation declined successfully"})

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        invitation = self.get_object()
        
        # Check if user has permission to withdraw (must be owner or co-owner)
        if not (request.user.owner and request.user.organization.id == invitation.organization.id) and \
        not (request.user.coowner == invitation.organization.id):
            return Response(
                {"error": "You don't have permission to withdraw this invitation"},
                status=status.HTTP_403_FORBIDDEN
            )

        if invitation.status != 'pending':
            return Response(
                {"error": "This invitation has already been processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Instead of updating status, just delete the invitation
        invitation.delete()

        return Response({"message": "Invitation withdrawn successfully"})

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        invitation = self.get_object()
        
        # Check if user has permission to resend (must be owner or co-owner)
        if not (request.user.owner and request.user.organization.id == invitation.organization.id) and \
        not (request.user.coowner == invitation.organization.id):
            return Response(
                {"error": "You don't have permission to resend this invitation"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate new token
        token = get_random_string(64)
        invitation.token = token
        invitation.created_at = timezone.now()
        invitation.status = 'pending'
        invitation.save()

        # Generate new invitation link
        invitation_link = f"{settings.FRONTEND_URL}/join-organization/{token}"
        
        try:
            send_invitation_email(
                invitation.email,
                invitation.organization.name,
                invitation_link
            )
            return Response({"message": "Invitation resent successfully"})
        except Exception as e:
            return Response(
                {"error": "Failed to resend invitation email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@permission_classes([AllowAny])
class ProcessInvitationView(APIView):
    def get(self, request, token):
        """Verify if invitation token is valid"""
        try:
            # Find invitation by token
            invitation = Invitation.objects.get(token=token)
            
            # Check if invitation is still pending
            if invitation.status != 'pending':
                return Response({
                    'status': 'error',
                    'message': 'This invitation has already been processed'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if invitation is expired (7 days)
            if invitation.created_at < timezone.now() - timedelta(days=7):
                return Response({
                    'status': 'error',
                    'message': 'This invitation has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'status': 'success',
                'organization_name': invitation.organization.name,
                'email': invitation.email
            })
            
        except Invitation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Invalid invitation token'
            }, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, token):
        """Accept or decline invitation"""
        try:
            invitation = Invitation.objects.get(token=token)
            action = request.data.get('action')
            if invitation.status != 'pending':
                return Response({
                    'status': 'error',
                    'message': 'This invitation has already been processed'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if invitation is expired
            if invitation.created_at < timezone.now() - timedelta(days=7):
                return Response({
                    'status': 'error',
                    'message': 'This invitation has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Try to find existing user with the invitation email
                user = User.objects.get(email=invitation.email)
            except User.DoesNotExist:
                if action == 'accept':
                    return Response({
                        'status': 'error',
                        'message': 'Please create an account first with the invited email',
                        'need_signup': True,
                        'email': invitation.email
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Delete declined invitation
                    invitation.delete()
                    return Response({
                        'status': 'success',
                        'message': 'Invitation declined successfully'
                    })
            
            if action == 'accept':
                # Update invitation status
                invitation.status = 'accepted'
                invitation.save()
                
                # Update user's organization
                user.organization = invitation.organization
                user.save()
                # Delete accepted invitation
                invitation.delete()
                
                return Response({
                    'status': 'success',
                    'message': 'Invitation accepted successfully'
                })
                
            elif action == 'decline':
                # Delete declined invitation
                invitation.delete()
                
                return Response({
                    'status': 'success',
                    'message': 'Invitation declined successfully'
                })
                
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid action'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Invitation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Invalid invitation token'
            }, status=status.HTTP_404_NOT_FOUND)


# for some reason need csrf exempt for the function idk why though CORS should have handled this
# Endpoint for verifying a user on the backend. Once a user has signed up on the VB website,
# An email will be sent for them to verify the account. Once sent the user clicks on the verify
# button which then goes through this endpoint to verify the user's account on the backend.
# This is done by setting the is_active and is_verified boolean variables for that user to be
# true. The designated the flow is that once clicked on verified it should take the user to the
# onboarding page. However, there was an issue with that as described in the code below.
@csrf_exempt
def activate(request):
    # get user
    try:
        user = User.objects.get(pk=request.GET.get('id'))
        token = request.GET.get('token')
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # verify user and token matches
    if user is not None and account_activation_token.check_token(user, token):
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        user.is_active = True  # account is now active
        user.is_verified = True  # account is now active
        user.save()

        # Potential error here as it does not log the user
        # on the frontend, because once redirected to the
        # onboarding page it shows the error that the
        # user must be signed in to access that page
        login(request, user)
        print(f"Session data after login: {request.session}")

        # Expected action: Redirect to the terms of use page after login
        # Current action: Right now it temporarily redirects the user
        # back to the login in page using a hardcoded
        # link for testing purposes. The correct
        # flow is to automatically login in the user
        # and send them right to the onboarding page
        # however, there was an issue that I was not
        # able to resolve in terms of the logining the user
        # as shown in the code above with login(request, user)

        frontend_url = f'http://localhost:3000/login/' # Need to edit the frontend link such that it is dynamic and
        # reflects the actual frontend url. The current link has been hardcoded just as a placeholder and for testing
        # purposes
        return HttpResponseRedirect(frontend_url)
    else:
        res = HttpResponse()
        res.status_code = 400
        return res

# Endpoint for reset password feature. This endpoint first used to the user an email,
# when they click on reset password on the front end. The email sent should contain another link to the actual
# page where the user can change their password. This endpoint is responsible for handling
# sending the email to the user and generating a unique token for security reasons
# ensuring the user gets a unique link to change their password. More details about this
# feature can be found here: https://docs.google.com/document/d/1yqCskeGixRoKEdxTHuHCmpTBfRlyfvntqPaIJDkFFu0/edit?usp=sharing
class ForgotPasswordView(UserMixin, generics.UpdateAPIView):
    model = User

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Need to edit the frontend link such that it is dynamic and reflects the actual frontend url
            # The current link has been hardcoded just as a placeholder and for testing purposes
            reset_link = f"http://frontend.com/password-reset-confirm?uid={uid}&token={token}"  # Needs to be built out on the frontend

            # Send reset email
            forgot_password(user, reset_link)
            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

# Endpoint for reset password feature. This endpoint handles updating the user's password
# on the backend. However, before the password is saved on the backend, it is hashed to
# ensure the integrity of the password is maintained. Once again, once the password
# has successfully been changed, a confirmation email is sent to the user notifying
# them of this.
# More details about this feature can be found here:
# https://docs.google.com/document/d/1yqCskeGixRoKEdxTHuHCmpTBfRlyfvntqPaIJDkFFu0/edit?usp=sharing
class ResetPasswordConfirmView(UserMixin, generics.UpdateAPIView):
    # permission_classes = [AllowAny]
    serializer_class = ChangePasswordSerializer
    model = User

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            # send email --> This also needs to be built out on the frontend. There is no html page
            # That reflects/corresponds to the succeful password has been changed message for the user
            change_password(self.object)

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Endpoint for the Google authentication and signup. This code extracts the authentication token from the URL,
# and then it authenticates that user on the backend. Once a user has been authenticated it logs them in on the
# backend (of course while sending the appropriate error messages). More detials about this feature can be found
# here: https://docs.google.com/document/d/1W-ZApjaZ75lwFNFrK60pI5l6vaya1cxsBZDWYaKRsVs/edit?usp=sharing
@csrf_exempt
class GoogleView(APIView):
    def post(self, request):
        """
        Handles Google authentication using an access token.
        """
        token = request.GET.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=400)

        strategy = load_strategy(request)
        backend = load_backend(strategy, "google-oauth2", redirect_uri=None)

        try:
            user = backend.do_auth(token)
        except AuthException as e:
            return Response({"error": "Invalid token or authentication failed"}, status=400)

        if user:
            login(request, user)
            return Response({"message": "Successfully authenticated", "user_id": user.id})
        return Response({"error": "Authentication failed"}, status=400)
