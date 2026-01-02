"""
Admin configuration for Prediction app.
"""
from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """Admin configuration for Prediction model."""

    list_display = [
        'student', 'risk_score', 'risk_level', 'predicted_success_rate',
        'model_version', 'created_at'
    ]
    list_filter = ['risk_level', 'created_at', 'model_version']
    search_fields = [
        'student__student_id',
        'student__first_name',
        'student__last_name'
    ]
    readonly_fields = ['risk_level', 'created_at', 'updated_at']
    ordering = ['-created_at']
