"""
Django admin configuration for core models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for audit logs.
    """
    list_display = [
        'id',
        'timestamp',
        'user_link',
        'action_display',
        'model_name',
        'object_repr',
        'ip_address',
        'status_code_display',
    ]
    list_filter = [
        'action',
        'model_name',
        'timestamp',
        'status_code',
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'model_name',
        'object_repr',
        'ip_address',
        'endpoint',
    ]
    readonly_fields = [
        'user',
        'action',
        'content_type',
        'object_id',
        'model_name',
        'object_repr',
        'changes',
        'ip_address',
        'user_agent',
        'timestamp',
        'endpoint',
        'method',
        'status_code',
        'extra_data',
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    list_per_page = 50

    fieldsets = (
        (_('Information de base'), {
            'fields': ('timestamp', 'user', 'action')
        }),
        (_('Objet affecté'), {
            'fields': ('content_type', 'object_id', 'model_name', 'object_repr')
        }),
        (_('Détails de la requête'), {
            'fields': ('endpoint', 'method', 'status_code')
        }),
        (_('Changements'), {
            'fields': ('changes',),
            'classes': ('collapse',)
        }),
        (_('Informations client'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Données supplémentaires'), {
            'fields': ('extra_data',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Disable adding audit logs through admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete audit logs."""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs."""
        return False

    def user_link(self, obj):
        """Display user as a link to the user admin."""
        if obj.user:
            return format_html(
                '<a href="/admin/users/user/{}/change/">{}</a>',
                obj.user.pk,
                obj.user.get_full_name()
            )
        return '-'
    user_link.short_description = _('Utilisateur')

    def action_display(self, obj):
        """Display action with color coding."""
        colors = {
            'create': '#28a745',
            'update': '#ffc107',
            'delete': '#dc3545',
            'login': '#17a2b8',
            'logout': '#6c757d',
            'permission_denied': '#dc3545',
            'error': '#dc3545',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_display.short_description = _('Action')

    def status_code_display(self, obj):
        """Display status code with color coding."""
        if not obj.status_code:
            return '-'

        if obj.status_code < 300:
            color = '#28a745'
        elif obj.status_code < 400:
            color = '#17a2b8'
        elif obj.status_code < 500:
            color = '#ffc107'
        else:
            color = '#dc3545'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status_code
        )
    status_code_display.short_description = _('Code statut')
