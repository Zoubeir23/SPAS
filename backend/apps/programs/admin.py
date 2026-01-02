"""
Admin configuration for Program app.
"""
from django.contrib import admin
from .models import Program, Subject


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Admin configuration for Program model."""

    list_display = ['code', 'name', 'duration', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['code']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin configuration for Subject model."""

    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['programs']
    ordering = ['code']

    fieldsets = (
        ('Informations de la matière', {
            'fields': ('code', 'name', 'description')
        }),
        ('Programmes', {
            'fields': ('programs',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
