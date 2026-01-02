"""
Admin configuration for Alert app.
"""
from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin configuration for Alert model."""

    list_display = [
        'student', 'type', 'level', 'status',
        'created_at'
    ]
    list_filter = ['type', 'level', 'status', 'created_at']
    search_fields = [
        'student__student_id',
        'student__first_name',
        'student__last_name',
        'message'
    ]
    readonly_fields = [
        'acknowledged_at',
        'resolved_at',
        'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
