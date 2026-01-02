"""
Admin configuration for Grade app.
"""
from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin configuration for Grade model."""

    list_display = [
        'student', 'subject', 'session', 'value', 'max_value',
        'type', 'date'
    ]
    list_filter = ['type', 'date', 'session']
    search_fields = [
        'student__student_id',
        'student__first_name',
        'student__last_name',
        'subject__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
