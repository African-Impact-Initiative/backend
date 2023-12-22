from rest_framework import serializers
from .models import Organization
from accounts.serializers import UserPublicSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    user_set = UserPublicSerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Organization
        fields = '__all__'

class AddChallengeSerializer(serializers.Serializer):
    model = Organization
    challenge1 = serializers.CharField(required=False)
    challenge2 = serializers.CharField(required=False)
    challenge3 = serializers.CharField(required=False)

class AddFundingSerializer(serializers.Serializer):
    model = Organization
    funding = serializers.CharField()

class AddStageSerializer(serializers.Serializer):
    model = Organization
    stage = serializers.CharField()