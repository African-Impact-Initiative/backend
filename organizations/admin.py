from django.contrib import admin
from .models import Organization, JoinRequest

admin.site.register(Organization)

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'organization__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'organization')