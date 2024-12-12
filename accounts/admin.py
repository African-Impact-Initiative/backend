from django.contrib import admin

from django.contrib.auth import get_user_model
from .models import Invitation
User = get_user_model()

admin.site.register(User)

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'organization', 'invited_by', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['email']