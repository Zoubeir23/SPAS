"""
Admin configuration for Session app.
"""
from django.contrib import admin
from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin configuration for Session model."""

    list_display = ['name', 'year', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'year']
    search_fields = ['name', 'year']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-year', '-start_date']
