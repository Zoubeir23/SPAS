"""
Admin configuration for Student app.
"""
from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin configuration for Student model."""

    list_display = [
        'matricule', 'first_name', 'last_name', 'email',
        'program', 'status', 'risk_level'
    ]
    list_filter = ['status', 'program', 'risk_level']
    search_fields = ['matricule', 'first_name', 'last_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['last_name', 'first_name']

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('matricule', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth')
        }),
        ('Informations académiques', {
            'fields': ('program', 'session', 'status')
        }),
        ('Évaluation du risque', {
            'fields': ('risk_level', 'risk_score')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
