"""
Views for Programs app.
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Program, Subject
from .serializers import ProgramSerializer, ProgramListSerializer


class ProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Program model.

    Provides CRUD operations and custom actions:
    - GET /programs/ - List all programs
    - POST /programs/ - Create a program
    - GET /programs/{id}/ - Retrieve a program
    - PUT/PATCH /programs/{id}/ - Update a program
    - DELETE /programs/{id}/ - Delete a program
    - GET /programs/{id}/students/ - Get all students in program
    """
    queryset = Program.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'code']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return ProgramListSerializer
        return ProgramSerializer

    def get_queryset(self):
        """Optimize queryset with prefetch_related."""
        queryset = Program.objects.prefetch_related('subjects', 'students')
        return queryset

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students in a program.

        GET /programs/{id}/students/
        """
        program = self.get_object()

        # Import here to avoid circular imports
        from apps.students.models import Student
        from apps.students.serializers import StudentListSerializer

        students = Student.objects.filter(
            program=program
        ).select_related('session').order_by('last_name', 'first_name')

        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subject model.

    Provides CRUD operations:
    - GET /subjects/ - List all subjects
    - POST /subjects/ - Create a subject
    - GET /subjects/{id}/ - Retrieve a subject
    - PUT/PATCH /subjects/{id}/ - Update a subject
    - DELETE /subjects/{id}/ - Delete a subject
    """
    queryset = Subject.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        """Optimize queryset with prefetch_related."""
        queryset = Subject.objects.prefetch_related('programs')

        # Filter by program if provided
        program_id = self.request.query_params.get('program', None)
        if program_id:
            queryset = queryset.filter(programs__id=program_id)

        return queryset
