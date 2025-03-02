from django.shortcuts import get_object_or_404
from rest_framework import generics
from accounts.serializers import UserPublicSerializer
from .models import Organization, JoinRequest
from django.db.models import Q
from .serializers import JoinRequestSerializer, OrganizationSerializer, AddChallengeSerializer, AddFundingSerializer, AddStageSerializer
from venturebuild.mixins import PublicResourceMixin, UserMixin, OwnerOnlyMixin, OwnerOrReadOnlyMixin
from venturebuild import settings
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.core.mail import EmailMessage



from django.contrib.auth import get_user_model
User = get_user_model()

# REST Framework very nice :) handles everything
class OrganizationListCreateAPIView(UserMixin, generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def perform_create(self, serializer):
        try:
            user = User.objects.get(id=self.request.user.id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if not user.terms_of_use:
            # build this response
            response = {
                'status': 'error',
                'code': status.HTTP_403_FORBIDDEN,
                'message': 'Must agree to terms of use before proceeding',
                'data': []
            }

            return Response(response)

        org = serializer.save()
        user.organization = org
        user.owner = True
        user.save()

    def filter_queryset(self, queryset):
        org = self.request.query_params.get('organization', None)
        industry = self.request.query_params.get('industry', None)

        if org or industry:
            query = None

            if org:
                query = Q(name__icontains=org) | Q(name__in=org.split(' '))
            if industry:
                industry_match = Q(industries__name__icontains=industry)
                query = industry_match if query is None else query | industry_match

            return self.queryset.filter(query).distinct()

        return super().filter_queryset(queryset)

class OrganizationViewUpdateDeleteAPIView(OwnerOrReadOnlyMixin, PublicResourceMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class UploadLogo(OwnerOrReadOnlyMixin, PublicResourceMixin, generics.UpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def post(self, request, *args, **kwargs):
        org = self.get_object()
        logo_file = request.FILES.get('logo')
        if logo_file:
            org.logo = logo_file
            org.save()
            serializer = self.get_serializer(org)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(message='Logo file not provided', status=status.HTTP_400_BAD_REQUEST)

class OrganizationByIdentifierView(UserMixin, PublicResourceMixin, generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = 'identifier'

class StageUpdate(OwnerOnlyMixin, PublicResourceMixin, generics.UpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = AddStageSerializer
    lookup_field = 'identifier'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if serializer.data.get("stage", False):
                org = self.get_object()
                org.stage = serializer.data.get("stage")
                org.save()

                # build this response
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Organization stage set',
                    'data': []
                }
            else:
                # build this response
                response = {
                    'status': 'error',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Stage not specified',
                    'data': []
                }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FundingUpdate(OwnerOnlyMixin, PublicResourceMixin, generics.UpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = AddFundingSerializer
    lookup_field = 'identifier'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if serializer.data.get("funding", False):
                org = self.get_object()
                org.funding = serializer.data.get("funding")
                org.save()

                # build this response
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Organization funding set',
                    'data': []
                }
            else:
                # build this response
                response = {
                    'status': 'error',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Funding not specified',
                    'data': []
                }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChallengeUpdate(OwnerOnlyMixin, generics.UpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = AddChallengeSerializer
    lookup_field = 'identifier'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            c1 = serializer.data.get("challenge1", False)
            c2 = serializer.data.get("challenge2", False)
            c3 = serializer.data.get("challenge3", False)
            if c1 or c2 or c3:
                org = self.get_object()
                if c1:
                    org.challenge1 = serializer.data.get("challenge1")
                    org.save()
                if c2:
                    org.challenge2 = serializer.data.get("challenge2")
                    org.save()
                if c3:
                    org.challenge3 = serializer.data.get("challenge3")
                    org.save()

                # build this response
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Organization challenges set',
                    'data': []
                }
            else:
                # build this response
                response = {
                    'status': 'error',
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Challenges not specified',
                    'data': []
                }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationMembersView(generics.ListAPIView):
    serializer_class = UserPublicSerializer

    def get_queryset(self):
        # Get the organization of the current user
        organization_id = self.kwargs.get('organization_id')
        if organization_id:
            # Return all users belonging to this organization
            return get_user_model().objects.all().filter(organization_id=organization_id)
        return get_user_model().objects.none()


class UpdateOrganizationMemberView(generics.UpdateAPIView):
    serializer_class = UserPublicSerializer
    
    def get_object(self):
        organization_id = self.kwargs.get('organization_id')
        user_id = self.kwargs.get('user_id')
        return get_user_model().objects.filter(
            organization_id=organization_id,
            id=user_id
        )


class UpdateMemberCoownerStatusView(OwnerOnlyMixin, generics.UpdateAPIView):
    serializer_class = UserPublicSerializer
    
    def get_object(self):
        organization_id = self.kwargs.get('organization_id')
        user_id = self.kwargs.get('user_id')
        return get_user_model().objects.get(
            organization_id=organization_id,
            id=user_id
        )
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        organization_id = self.kwargs.get('organization_id')
        
        if user.coowner == organization_id:
            user.coowner = None
        else:
            user.coowner = organization_id
            
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JoinRequestViewSet(viewsets.ModelViewSet):
    queryset = JoinRequest.objects.all()
    serializer_class = JoinRequestSerializer

    def create(self, request, *args, **kwargs):
        # Check if user already has a pending request
        if JoinRequest.objects.filter(user=request.user, status='pending').exists():
            return Response(
                {"error": "You already have a pending join request"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is already in an organization
        if request.user.organization:
            return Response(
                {"error": "You are already a member of an organization"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create join request
        organization_id = request.data.get('organization')
        organization = get_object_or_404(Organization, id=organization_id)

        # Create join request using the serializer
        serializer = self.get_serializer(data={'organization': organization_id})
        serializer.is_valid(raise_exception=True)
        join_request = serializer.save(user=request.user)

        # Now, send an email notification to the organization's admin(s) and cc all co-owners.
        # Query organization admins (owners)
        admin_users = User.objects.filter(organization=organization, owner=True)
        # Query co-owners (assuming coowner field equals the organization id)
        coowners = User.objects.filter(organization=organization, coowner=organization.id)

        subject = "New Join Request for Your Organization"
        message = (
            f"Hello,\n\n"
            f"{request.user.get_full_name()} has requested to join your organization "
            f"{organization.name}.\n\n"
            "Please log in to the dashboard for further details.\n\n"
            "Thank you."
        )
        # Build recipient lists
        recipient_list = [admin.email for admin in admin_users if admin.email]
        cc_list = [user.email for user in coowners if user.email]

        # You can either use send_mail directly...
        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER,  # Ensure this is set in your settings
                to=recipient_list,
                cc=cc_list
            )
            email.send(fail_silently=False)
        except Exception as e:
            # Log the error (you might want to handle this more gracefully)
            print("Error sending join request email:", e)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        join_request = self.get_object()
        
        # Check if user has permission to accept (must be owner or co-owner)
        if not (request.user.owner and request.user.organization.id == join_request.organization.id) and \
           not (request.user.coowner == join_request.organization.id):
            return Response(
                {"error": "You don't have permission to accept join requests"},
                status=status.HTTP_403_FORBIDDEN
            )

        if join_request.status != 'pending':
            return Response(
                {"error": "This request has already been processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update request status
        join_request.status = 'accepted'
        join_request.save()

        # Update user's organization
        join_request.user.organization = join_request.organization
        join_request.user.save()
        # Delete the join request record from the database.
        join_request.delete()

        return Response({"message": "Join request accepted successfully"})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        join_request = self.get_object()
        
        # Check if user has permission to decline
        if not (request.user.owner and request.user.organization.id == join_request.organization.id) and \
           not (request.user.coowner == join_request.organization.id):
            return Response(
                {"error": "You don't have permission to decline join requests"},
                status=status.HTTP_403_FORBIDDEN
            )

        if join_request.status != 'pending':
            return Response(
                {"error": "This request has already been processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        join_request.status = 'declined'
        join_request.save()

        # Delete the join request record from the database.
        join_request.delete()

        return Response({"message": "Join request declined successfully"})
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's join request"""
        try:
            join_request = JoinRequest.objects.get(
                user=request.user,
                status='pending'
            )
            serializer = self.get_serializer(join_request)
            return Response(serializer.data)
        except JoinRequest.DoesNotExist:
            return Response(None)