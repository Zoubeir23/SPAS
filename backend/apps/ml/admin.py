"""
Admin configuration for ML app.
"""
from django.contrib import admin
from .models import MLModel


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    """Admin configuration for MLModel model."""

    list_display = [
        'name', 'version', 'status', 'accuracy',
        'precision', 'recall', 'f1_score', 'trained_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'version']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-trained_at', '-created_at']
