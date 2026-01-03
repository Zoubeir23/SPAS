"""
Serializers for Program app.
"""
from rest_framework import serializers
from .models import Department, Program, Subject


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""

    program_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'description', 'status',
            'program_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_program_count(self, obj):
        """Get number of active programs in department."""
        return obj.programs.filter(status='active').count()


class DepartmentListSerializer(serializers.ModelSerializer):
    """Minimal serializer for department lists."""

    program_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'status', 'program_count']

    def get_program_count(self, obj):
        """Get number of active programs in department."""
        return obj.programs.filter(status='active').count()


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program model."""

    student_count = serializers.SerializerMethodField()
    department = DepartmentListSerializer(read_only=True)
    department_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Program
        fields = [
            'id', 'code', 'name', 'description', 'duration',
            'status', 'department', 'department_id', 'student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create program with department."""
        department_id = validated_data.pop('department_id', None)
        if department_id:
            validated_data['department_id'] = department_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update program with department."""
        department_id = validated_data.pop('department_id', None)
        if department_id is not None:
            validated_data['department_id'] = department_id
        return super().update(instance, validated_data)

    def get_student_count(self, obj):
        """Get number of active students in program."""
        return obj.students.filter(status='active').count()


class ProgramListSerializer(serializers.ModelSerializer):
    """Minimal serializer for program lists."""

    department = DepartmentListSerializer(read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'code', 'name', 'status', 'department']


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
