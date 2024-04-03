from rest_framework import serializers
from .models import Organization
from accounts.serializers import UserPublicSerializer
from django_countries.serializer_fields import CountryField
from taggit.serializers import (TagListSerializerField, TaggitSerializer)

class OrganizationSerializer(TaggitSerializer, serializers.ModelSerializer):
    industries = TagListSerializerField(required=False)
    location = CountryField(name_only=True, required=False, allow_null=True)

    user_set = UserPublicSerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Organization
        fields = '__all__'
    
    def validate_website(self, value):
        # website URL has to be unique, empty string is not unique
        if value == '':
            return None
        return value
    
    def validate_linkedin(self, value):
        # linkedin URL has to be unique, empty string is not unique
        if value == '':
            return None
        return value
    
    def validate_twitter(self, value):
        # twitter URL has to be unique, empty string is not unique
        if value == '':
            return None
        return value
    
    def validate_facebook(self, value):
        # facebook URL has to be unique, empty string is not unique
        if value == '':
            return None
        return value
    
    def validate_instagram(self, value):
        # instagram URL has to be unique, empty string is not unique
        if value == '':
            return None
        return value

class AddChallengeSerializer(serializers.Serializer):
    model = Organization
    challenge1 = serializers.ChoiceField(choices=Organization.Challenges.CHOICES)
    challenge2 = serializers.ChoiceField(choices=Organization.Challenges.CHOICES)
    challenge3 = serializers.ChoiceField(choices=Organization.Challenges.CHOICES)

class AddFundingSerializer(serializers.Serializer):
    model = Organization
    funding = serializers.ChoiceField(choices=Organization.Funding.CHOICES)

class AddStageSerializer(serializers.Serializer):
    model = Organization
    stage = serializers.ChoiceField(choices=Organization.Stages.CHOICES)