from django.db import models
from django.db.models import Q
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields

from organizations.models import Organization
# from django.dispatch import receiver
# from django_rest_passwordreset.signals import reset_password_token_created

import os

def get_dir(instance, filename):
    return f'photos/{instance.id}/{filename}'

# Manager used when creating users
class UserManager(BaseUserManager):
    # Regular user
    def create_user(self, email, password=None, first_name=None, last_name=None):
        # Mandatory to have an emai,
        if not email:
            raise ValueError('Users must have an email address')

        # create user
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        # TODO implement Google OAUTH
        # reason to check is because Google users have no password
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()    # marks that the user has no password

        # save user
        user.save(using=self._db)
        return user

    # staff user NOT Django Superuser
    def create_staffuser(self, email, password=None, first_name=None, last_name=None):
        # use the regular user method above to create user
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # only set staff to true not admin (for superuser only)
        user.staff = True
        user.save(using=self._db)
        return user

    # superuser for Django and Resource Hub (user can manage and create new admins)
    def create_superuser(self, email, password=None, first_name=None, last_name=None):
        # use the regular user method above to create user
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # only set staff and admin to true
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user

# User class
class User(AbstractBaseUser):
    objects = UserManager()

    # User properties (no need to include password Django handles this)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)

    # cannot use is_active to verify account since user is unable to log
    # in if set to false, we still want users to have log in functionality
    # for the 3 day period if they are not verified
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)    # used to verify user account
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    joined = models.DateTimeField(auto_now_add=True) # used in cron job to check when to delete user account

    terms_of_use = models.BooleanField(default=False)
    linkedin = models.URLField(blank=True, null=True, unique=True)
    photo = models.ImageField(null=True, blank=True, upload_to=get_dir)
    role = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    bio = models.CharField(null=True, blank=True, max_length=300)

    organizations = models.ManyToManyField(Organization, blank=True)

    # Users email will be used as username
    USERNAME_FIELD = 'email'
    # Note password and email not included, it is automatically mandatory by Django
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return f'{self.get_full_name()}: {self.email}'

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

# when password reset token is created this function will run
# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
#     # send email to user with link to reset password
#     from resource_hub.email_server import forgot_password
#     link = f"{os.environ.get('FRONTEND_URL')}/confirm-forgot-password/?token={reset_password_token.key}"
#     forgot_password(reset_password_token.user, link)
