"""
Serializers for ML app.
"""
from rest_framework import serializers
from .models import MLModel, TrainingJob


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer for MLModel model."""

    average_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = MLModel
        fields = [
            'id', 'name', 'version', 'status',
            'accuracy', 'precision', 'recall', 'f1_score', 'average_score',
            'trained_at', 'training_data_size',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MLModelListSerializer(serializers.ModelSerializer):
    """Minimal serializer for ML model lists."""

    class Meta:
        model = MLModel
        fields = ['id', 'name', 'version', 'status', 'accuracy', 'trained_at']


class TrainingJobSerializer(serializers.ModelSerializer):
    """Full serializer for TrainingJob."""

    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    resulting_model_name = serializers.CharField(source='resulting_model.name', read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = TrainingJob
        fields = [
            'id', 'name', 'description', 'job_type', 'status',
            'algorithm', 'hyperparameters', 'features',
            'progress', 'current_step', 'logs',
            'resulting_model', 'resulting_model_name',
            'error_message',
            'started_at', 'completed_at', 'duration_seconds',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'progress', 'current_step', 'logs',
            'resulting_model', 'error_message',
            'started_at', 'completed_at',
            'created_at', 'updated_at'
        ]

    def get_duration_seconds(self, obj):
        """Calculate training duration in seconds."""
        if obj.started_at and obj.completed_at:
            delta = obj.completed_at - obj.started_at
            return delta.total_seconds()
        return None


class TrainingJobListSerializer(serializers.ModelSerializer):
    """Minimal serializer for TrainingJob list."""

    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = TrainingJob
        fields = [
            'id', 'name', 'job_type', 'status', 'algorithm',
            'progress', 'created_by_name', 'created_at'
        ]


class TrainingJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a TrainingJob."""

    class Meta:
        model = TrainingJob
        fields = [
            'name', 'description', 'job_type',
            'algorithm', 'hyperparameters', 'features'
        ]

    def validate_algorithm(self, value):
        """Validate algorithm choice."""
        valid_algorithms = ['random_forest', 'gradient_boosting', 'logistic_regression']
        if value not in valid_algorithms:
            raise serializers.ValidationError(
                f"Algorithm must be one of: {', '.join(valid_algorithms)}"
            )
        return value


class RiskPredictionRequestSerializer(serializers.Serializer):
    """Serializer for risk prediction request."""

    student_id = serializers.UUIDField(required=True)


class BulkRiskPredictionRequestSerializer(serializers.Serializer):
    """Serializer for bulk risk prediction request."""

    student_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of student IDs. If empty, predicts for all students."
    )
    program_id = serializers.UUIDField(
        required=False,
        help_text="Filter students by program."
    )
    risk_threshold = serializers.FloatField(
        required=False,
        min_value=0,
        max_value=100,
        default=50,
        help_text="Minimum risk score to include in results."
    )
