"""
Views for Sessions app.
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Session
from .serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Session model.

    Provides CRUD operations and custom actions:
    - GET /sessions/ - List all sessions
    - POST /sessions/ - Create a session
    - GET /sessions/{id}/ - Retrieve a session
    - PUT/PATCH /sessions/{id}/ - Update a session
    - DELETE /sessions/{id}/ - Delete a session
    - GET /sessions/{id}/students/ - Get all students in session
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'year']
    search_fields = ['name', 'year']
    ordering_fields = ['year', 'start_date', 'created_at']
    ordering = ['-year', '-start_date']

    def get_queryset(self):
        """Optimize queryset with prefetch_related."""
        queryset = Session.objects.prefetch_related('students')
        return queryset

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """
        Get all students in a session.

        GET /sessions/{id}/students/
        """
        session = self.get_object()

        # Import here to avoid circular imports
        from apps.students.models import Student
        from apps.students.serializers import StudentListSerializer

        students = Student.objects.filter(
            session=session
        ).select_related('program').order_by('last_name', 'first_name')

        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)
