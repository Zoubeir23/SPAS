"""
Serializers for Program app.
"""
from rest_framework import serializers
from .models import Program, Subject


class ProgramSerializer(serializers.ModelSerializer):
    """Full serializer for Program model."""

    student_count = serializers.SerializerMethodField()
    active_student_count = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = [
            'id', 'code', 'name', 'description', 'duration',
            'status', 'student_count', 'active_student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_count(self, obj):
        """Get total number of students in program."""
        return obj.students.count()

    def get_active_student_count(self, obj):
        """Get number of active students in program."""
        return obj.students.filter(status='active').count()


class ProgramListSerializer(serializers.ModelSerializer):
    """Minimal serializer for program lists."""

    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ['id', 'code', 'name', 'status', 'student_count']

    def get_student_count(self, obj):
        """Get number of active students in program."""
        return obj.students.filter(status='active').count()


class ProgramCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating programs."""

    class Meta:
        model = Program
        fields = ['code', 'name', 'description', 'duration', 'status']

    def validate_code(self, value):
        """Validate that program code is unique."""
        if self.instance:
            if Program.objects.filter(code=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Un programme avec ce code existe déjà.")
        else:
            if Program.objects.filter(code=value).exists():
                raise serializers.ValidationError("Un programme avec ce code existe déjà.")
        return value


class SubjectSerializer(serializers.ModelSerializer):
    """Full serializer for Subject model."""

    program_codes = serializers.SerializerMethodField()
    program_names = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id', 'code', 'name', 'description',
            'programs', 'program_codes', 'program_names',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_program_codes(self, obj):
        """Get list of program codes."""
        return [program.code for program in obj.programs.all()]

    def get_program_names(self, obj):
        """Get list of program names."""
        return [program.name for program in obj.programs.all()]


class SubjectListSerializer(serializers.ModelSerializer):
    """Minimal serializer for subject lists."""

    program_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'program_count']

    def get_program_count(self, obj):
        """Get number of programs using this subject."""
        return obj.programs.count()


class SubjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating subjects."""

    class Meta:
        model = Subject
        fields = ['code', 'name', 'description', 'programs']

    def validate_code(self, value):
        """Validate that subject code is unique."""
        if self.instance:
            if Subject.objects.filter(code=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Une matière avec ce code existe déjà.")
        else:
            if Subject.objects.filter(code=value).exists():
                raise serializers.ValidationError("Une matière avec ce code existe déjà.")
        return value
