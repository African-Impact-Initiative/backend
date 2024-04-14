from rest_framework import serializers

from django.core import exceptions
import django.contrib.auth.password_validation as validators
from django_countries.serializer_fields import CountryField
from taggit.serializers import (TagListSerializerField, TaggitSerializer)

from organizations.models import Organization

from django.contrib.auth import get_user_model
User = get_user_model()

# Allow all fields except password
#! Danger never allow a post or put to this serializer (anyone can modify staff or admin)
class GetUserSerializer(TaggitSerializer, serializers.ModelSerializer):
    team = TagListSerializerField(required=False)
    country = CountryField(name_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        exclude = ['password', 'is_verified']

# Only allow id, email, name
class UserPublicSerializer(TaggitSerializer, serializers.ModelSerializer):
    team = TagListSerializerField(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'photo', 'role', 'leadership', 'team']

#! Danger never allow GET on this serializer user can see password
class UserSerializer(TaggitSerializer, serializers.ModelSerializer):
    team = TagListSerializerField(required=False)
    country = CountryField(name_only=True, required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')

        # since this is for POST and PUT only want admin to be able to set the staff and admin fields
        if not request or request.user is None or not request.user.is_staff:
            self.fields.pop('staff')
            self.fields.pop('admin')

        if not request or request.method == 'PUT':
            self.fields.pop('password')
            self.fields.pop('email')

    # make sure password complies with django basic requirements
    def validate_password(self, value):
        errors = dict()
        try:
            # validate the password and catch the exception
            validators.validate_password(password=value)
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return value

    class Meta:
        model = User
        exclude = ['is_verified']

# Used to change password
class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    # make sure new password complies with django basic requirements
    def validate_new_password(self, value):
        errors = dict()
        try:
            # validate the password and catch the exception
            validators.validate_password(password=value)
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return value

# Used to change email
class ChangeEmailSerializer(serializers.Serializer):
    model = User
    password = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension

# Used to update personal info
class UpdatePersonalInfo(serializers.Serializer):
    model = User
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.CharField(required=True)

    linkedin = serializers.URLField(required=False, allow_blank=True)
    photo = Base64ImageField(required=False)
    country = CountryField(name_only=True, required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)

# Used to agree to terms
class TermsOfUseAgreement(serializers.Serializer):
    model = User
    terms = serializers.BooleanField(required=True)

# Used to agree to terms
class AddOrganization(serializers.Serializer):
    model = User
    org = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())


