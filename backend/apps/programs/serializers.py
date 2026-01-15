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
        extra_kwargs = {
            'code': {
                'error_messages': {
                    'required': 'Le code du département est requis.',
                    'unique': 'Un département avec ce code existe déjà.',
                    'max_length': 'Le code ne peut pas dépasser 20 caractères.'
                }
            },
            'name': {
                'error_messages': {
                    'required': 'Le nom du département est requis.',
                    'unique': 'Un département avec ce nom existe déjà.',
                    'max_length': 'Le nom ne peut pas dépasser 200 caractères.'
                }
            }
        }

    def validate_code(self, value):
        """Validate department code format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Le code du département ne peut pas être vide.")
        return value.strip().upper()

    def validate_name(self, value):
        """Validate department name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du département ne peut pas être vide.")
        return value.strip()

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
    department_id = serializers.UUIDField(
        write_only=True,
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'L\'ID du département n\'est pas valide.',
            'does_not_exist': 'Le département sélectionné n\'existe pas.'
        }
    )

    class Meta:
        model = Program
        fields = [
            'id', 'code', 'name', 'description', 'duration',
            'status', 'department', 'department_id', 'student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'code': {
                'error_messages': {
                    'required': 'Le code de la filière est requis.',
                    'unique': 'Une filière avec ce code existe déjà.',
                    'max_length': 'Le code ne peut pas dépasser 20 caractères.'
                }
            },
            'name': {
                'error_messages': {
                    'required': 'Le nom de la filière est requis.',
                    'max_length': 'Le nom ne peut pas dépasser 200 caractères.'
                }
            },
            'duration': {
                'error_messages': {
                    'required': 'La durée est requise.',
                    'invalid': 'La durée doit être un nombre entier positif.'
                }
            }
        }

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
