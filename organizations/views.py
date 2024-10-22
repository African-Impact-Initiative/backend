from rest_framework import generics

from .models import Organization
from django.db.models import Q
from .serializers import OrganizationSerializer, AddChallengeSerializer, AddFundingSerializer, AddStageSerializer
from venturebuild.mixins import PublicResourceMixin, UserMixin, OwnerOnlyMixin, OwnerOrReadOnlyMixin

from rest_framework.response import Response
from rest_framework import status

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