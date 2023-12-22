from rest_framework import generics

from .models import Organization
from .serializers import OrganizationSerializer, AddChallengeSerializer, AddFundingSerializer, AddStageSerializer
from venturebuild.mixins import PublicResourceMixin, UserMixin

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

        if not user.terms_of_use or not user.role:
                # build this response
                response = {
                    'status': 'error',
                    'code': status.HTTP_403_FORBIDDEN,
                    'message': 'Must agree to terms of use before proceeding',
                    'data': []
                }

                return Response(response)

        org = serializer.save()
        user.organizations.add(org)
        user.save()

class OrganizationViewUpdateDeleteAPIView(UserMixin, PublicResourceMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class OrganizationByIdentifierView(UserMixin, PublicResourceMixin, generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = 'identifier'

class StageUpdate(UserMixin, PublicResourceMixin, generics.UpdateAPIView):
    serializer_class = AddStageSerializer
    model = User
    lookup_field = 'identifier'

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(owner=user.id)

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

class FundingUpdate(UserMixin, PublicResourceMixin, generics.UpdateAPIView):
    serializer_class = AddFundingSerializer
    model = User
    lookup_field = 'identifier'

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(owner=user.id)

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

class ChallengeUpdate(UserMixin, generics.UpdateAPIView):
    serializer_class = AddChallengeSerializer
    model = User
    lookup_field = 'identifier'

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(owner=user.id)

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