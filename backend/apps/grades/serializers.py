"""
Serializers for Grade app.
"""
from rest_framework import serializers
from .models import Grade


class GradeSerializer(serializers.ModelSerializer):
    """Serializer for Grade model."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'student_matricule',
            'subject', 'subject_name', 'subject_code',
            'session', 'session_name',
            'value', 'max_value', 'percentage', 'type', 'date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_percentage(self, obj):
        """Calculate grade percentage."""
        if obj.max_value and obj.max_value > 0:
            return round((float(obj.value) / float(obj.max_value)) * 100, 2)
        return 0


class GradeListSerializer(serializers.ModelSerializer):
    """Minimal serializer for grade lists."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'student_name', 'subject_code', 'value', 'max_value', 'type', 'date']


class GradeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating grades."""

    class Meta:
        model = Grade
        fields = ['student', 'subject', 'session', 'value', 'max_value', 'type', 'date']
