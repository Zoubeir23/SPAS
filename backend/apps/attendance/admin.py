"""
Admin configuration for Attendance app.
"""
from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model."""

    list_display = ['student', 'subject', 'date', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = [
        'student__student_id',
        'student__first_name',
        'student__last_name',
        'subject__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
