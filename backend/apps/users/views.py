"""
Views for Users app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from .serializers import UserSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.

    Provides CRUD operations and custom actions:
    - GET /users/ - List all users
    - POST /users/ - Create a user
    - GET /users/{id}/ - Retrieve a user
    - PUT/PATCH /users/{id}/ - Update a user
    - DELETE /users/{id}/ - Delete a user
    - POST /users/{id}/change-password/ - Change user password
    - GET /users/me/ - Get current user profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'created_at', 'last_name']
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        # Only 'me' endpoint is accessible to all authenticated users
        # All other actions (list, retrieve, create, update, delete) require admin
        if self.action == 'me':
            return [IsAuthenticated()]
        # All other actions require admin privileges
        return [IsAdminUser()]

    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        """
        Change password for a specific user.

        POST /users/{id}/change-password/
        Body: {
            "old_password": "current_password",
            "new_password": "new_password"
        }
        """
        user = self.get_object()

        # Only allow users to change their own password or admins
        if request.user != user and not request.user.is_staff:
            return Response(
                {'error': 'You can only change your own password'},
                status=status.HTTP_403_FORBIDDEN
            )

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check old password
        if not user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate new password length
        if len(new_password) < 8:
            return Response(
                {'error': 'New password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile.

        GET /users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a user account.

        POST /users/{id}/activate/
        """
        user = self.get_object()
        user.is_active = True
        user.save()

        return Response({
            'success': True,
            'message': f'User {user.email} has been activated'
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account.

        POST /users/{id}/deactivate/
        """
        user = self.get_object()

        # Prevent deactivating yourself
        if user == request.user:
            return Response(
                {'error': 'You cannot deactivate your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = False
        user.save()

        return Response({
            'success': True,
            'message': f'User {user.email} has been deactivated'
        })
