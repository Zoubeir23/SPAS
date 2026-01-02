"""
Serializers for Alert app.
"""
from rest_framework import serializers
from .models import Alert, Intervention


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)
    program_name = serializers.CharField(source='student.program.name', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'student', 'student_name', 'student_matricule', 'program_name',
            'type', 'level', 'status', 'message',
            'acknowledged_at', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'acknowledged_at', 'resolved_at',
            'created_at', 'updated_at'
        ]


class AlertListSerializer(serializers.ModelSerializer):
    """Minimal serializer for alert lists."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'student_matricule', 'student_name',
            'type', 'level', 'status', 'message',
            'created_at'
        ]


class InterventionSerializer(serializers.ModelSerializer):
    """Full serializer for Intervention model."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)
    responsible_name = serializers.CharField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Intervention
        fields = [
            'id', 'student', 'student_name', 'student_matricule',
            'alert', 'type', 'type_display',
            'priority', 'priority_display',
            'status', 'status_display',
            'description', 'scheduled_date', 'completed_date',
            'responsible', 'responsible_name',
            'notes', 'outcome',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InterventionListSerializer(serializers.ModelSerializer):
    """Minimal serializer for intervention lists."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    responsible_name = serializers.CharField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Intervention
        fields = [
            'id', 'student', 'student_name',
            'type', 'type_display', 'priority', 'status',
            'scheduled_date', 'responsible_name',
            'created_at'
        ]


class InterventionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating interventions."""

    class Meta:
        model = Intervention
        fields = [
            'student', 'alert', 'type', 'priority',
            'description', 'scheduled_date', 'responsible'
        ]
