"""
Serializers for Prediction app.
"""
from rest_framework import serializers
from .models import Prediction


class PredictionSerializer(serializers.ModelSerializer):
    """Serializer for Prediction model."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)
    model_version_name = serializers.SerializerMethodField()
    top_factors = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = [
            'id', 'student', 'student_name', 'student_matricule',
            'model_version', 'model_version_name',
            'risk_score', 'risk_level', 'predicted_success_rate',
            'factors', 'top_factors',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'risk_level', 'created_at', 'updated_at']

    def get_model_version_name(self, obj):
        """Get model version string."""
        if obj.model_version:
            return f"{obj.model_version.name} v{obj.model_version.version}"
        return None

    def get_top_factors(self, obj):
        """Get top contributing factors."""
        return obj.get_top_factors(limit=5)


class PredictionListSerializer(serializers.ModelSerializer):
    """Minimal serializer for prediction lists."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)

    class Meta:
        model = Prediction
        fields = [
            'id', 'student_matricule', 'student_name',
            'risk_score', 'risk_level', 'predicted_success_rate',
            'created_at'
        ]
