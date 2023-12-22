from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from . import settings

from django.contrib.auth import get_user_model
User = get_user_model()

def welcome_email(user, link):
    email_subject = "Welcome to Venture Build"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/welcome.html',{
        'name': user.name,
        'link': link,
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def notify_admin(user, resource_name):
    email_subject = "A request was submitted"
    to_list = []

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/admin-notif.html',{
        'requester_name': user.name,
        'resource_name': resource_name
    })

    admins = User.objects.filter(staff=True).all()

    for admin in admins:
        to_list.append(admin.email)

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, to_list)
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def request_resource(user, resource_name):
    email_subject = "Your request has been submitted"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/request.html',{
        'name': user.name,
        'resource_name': resource_name
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def reject_resource(user, resource_name):
    email_subject = "Your request has been rejected"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/request-rejected.html', {
        'name': user.name,
        'resource_name': resource_name
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def approve_resource(user, resource_name):
    email_subject = "Your request has been approved"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/request-approved.html', {
        'name': user.name,
        'resource_name': resource_name
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def forgot_password(user, link):
    email_subject = "Reset your password"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/forgot-password.html', {
        'name': user.name,
        'link': link
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def change_password(user):
    email_subject = "Your password was changed"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/change-password.html', {
        'name': user.name,
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def change_email(user):
    email_subject = "Your email was changed"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/change-email.html', {
        'name': user.name,
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def promote(user):
    email_subject = "Your account was promoted"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/staff.html', {
        'name': user.name,
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def demote(user):
    email_subject = "Your account was demoted"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/demoted.html', {
        'name': user.name,
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()

def account_deleted(user):
    email_subject = "Your account has been deleted"

    # converts the html template so that you can send as email
    # it can be treated as regular django template so I can pass in context objs
    message = render_to_string('venture_build/account-deleted.html', {
        'name': user.name,
    })

    email = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
    email.fail_silently = True
    email.content_subtype = "html"
    email.send()
