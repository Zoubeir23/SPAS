"""
Serializers for Program app.
"""
from rest_framework import serializers
from .models import Program, Subject


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program model."""

    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = [
            'id', 'code', 'name', 'description', 'duration',
            'status', 'student_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_count(self, obj):
        """Get number of active students in program."""
        return obj.students.filter(status='active').count()


class ProgramListSerializer(serializers.ModelSerializer):
    """Minimal serializer for program lists."""

    class Meta:
        model = Program
        fields = ['id', 'code', 'name', 'status']


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model."""

    program_names = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id', 'code', 'name', 'description',
            'programs', 'program_names', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_program_names(self, obj):
        """Get list of program names."""
        return [p.name for p in obj.programs.all()]


class SubjectListSerializer(serializers.ModelSerializer):
    """Minimal serializer for subject lists."""

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name']
