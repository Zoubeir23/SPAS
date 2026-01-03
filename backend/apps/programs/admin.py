"""
Admin configuration for Program app.
"""
from django.contrib import admin
from .models import Department, Program, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for Department model."""

    list_display = ['code', 'name', 'status', 'program_count']
    list_filter = ['status', 'created_at']
    search_fields = ['code', 'name']
    readonly_fields = ['created_at', 'updated_at', 'program_count']
    ordering = ['code']

    def program_count(self, obj):
        """Display number of programs in department."""
        return obj.programs.count()
    program_count.short_description = 'Nombre de filières'


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Admin configuration for Program model."""

    list_display = ['code', 'name', 'department', 'duration', 'status']
    list_filter = ['status', 'department', 'created_at']
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
