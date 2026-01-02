"""
Reusable mixins for Django REST Framework ViewSets.

These mixins provide common functionality:
- RoleBasedPermissionMixin: Apply different permissions based on actions
- AuditLogMixin: Automatically log actions to the audit trail
- SoftDeleteMixin: Implement soft deletion for ViewSets
- QuerySetFilterMixin: Filter querysets based on user role
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import AuditLog
from .utils import get_client_ip


class RoleBasedPermissionMixin:
    """
    Mixin to apply different permissions based on the action being performed.

    This allows fine-grained control over who can perform what actions.

    Usage:
        class MyViewSet(RoleBasedPermissionMixin, viewsets.ModelViewSet):
            permission_classes_by_action = {
                'list': [IsAuthenticated],
                'retrieve': [IsAuthenticated],
                'create': [IsTeacherOrAdmin],
                'update': [IsOwnerOrReadOnly],
                'destroy': [IsAdmin],
                'custom_action': [IsDSOrAdmin],
            }

    If an action is not specified, it falls back to the default permission_classes.
    """

    permission_classes_by_action = {}

    def get_permissions(self):
        """
        Return the list of permissions based on the action being performed.
        """
        try:
            # Get permissions for specific action
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except (KeyError, AttributeError):
            # Fall back to default permissions
            return super().get_permissions()


class AuditLogMixin:
    """
    Mixin to automatically create audit log entries for actions.

    This creates a comprehensive audit trail of all operations.

    Usage:
        class MyViewSet(AuditLogMixin, viewsets.ModelViewSet):
            audit_log_actions = ['create', 'update', 'destroy']
            # or
            audit_log_all = True  # Log all actions

    The mixin will automatically log:
    - Who performed the action
    - What action was performed
    - What object was affected
    - When it was performed
    - From which IP address
    """

    # Actions to log (if not logging all)
    audit_log_actions = ['create', 'update', 'destroy', 'partial_update']

    # Whether to log all actions (including list and retrieve)
    audit_log_all = False

    # Whether to log the changes made
    audit_log_changes = True

    def should_audit_log(self, action_name=None):
        """
        Determine if the current action should be logged.
        """
        if self.audit_log_all:
            return True

        action_name = action_name or self.action
        return action_name in self.audit_log_actions

    def create_audit_log(self, action_type, instance=None, changes=None, extra_data=None):
        """
        Create an audit log entry.
        """
        request = self.request

        # Get IP address
        ip_address = get_client_ip(request)

        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        # Get endpoint and method
        endpoint = request.path
        method = request.method

        # Create audit log
        AuditLog.log_action(
            user=request.user if request.user.is_authenticated else None,
            action=action_type,
            content_object=instance,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            extra_data=extra_data
        )

    def perform_create(self, serializer):
        """Override to add audit logging for create actions."""
        if self.should_audit_log('create'):
            instance = serializer.save()

            # Get changes if enabled
            changes = None
            if self.audit_log_changes:
                changes = serializer.validated_data

            self.create_audit_log(
                action_type=AuditLog.Action.CREATE,
                instance=instance,
                changes=changes
            )
        else:
            super().perform_create(serializer)

    def perform_update(self, serializer):
        """Override to add audit logging for update actions."""
        if self.should_audit_log('update') or self.should_audit_log('partial_update'):
            # Get original data
            original_data = {}
            if self.audit_log_changes and serializer.instance:
                for field in serializer.validated_data.keys():
                    original_data[field] = getattr(serializer.instance, field, None)

            instance = serializer.save()

            # Get changes
            changes = None
            if self.audit_log_changes:
                changes = {
                    'before': original_data,
                    'after': serializer.validated_data
                }

            self.create_audit_log(
                action_type=AuditLog.Action.UPDATE,
                instance=instance,
                changes=changes
            )
        else:
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        """Override to add audit logging for delete actions."""
        if self.should_audit_log('destroy'):
            # Store object representation before deletion
            object_repr = str(instance)
            model_name = instance.__class__.__name__

            # Get object data
            changes = None
            if self.audit_log_changes:
                changes = {'deleted_object': object_repr}

            # Delete the instance
            super().perform_destroy(instance)

            # Log the deletion (without content_object since it's deleted)
            self.create_audit_log(
                action_type=AuditLog.Action.DELETE,
                instance=None,
                changes=changes,
                extra_data={
                    'model_name': model_name,
                    'object_repr': object_repr
                }
            )
        else:
            super().perform_destroy(instance)


class SoftDeleteMixin:
    """
    Mixin to implement soft deletion in ViewSets.

    This mixin changes the destroy action to soft-delete instead of hard-delete.
    It also adds actions to restore and permanently delete objects.

    Usage:
        class MyViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
            # Your viewset code

        # Soft delete (default destroy action)
        DELETE /api/mymodel/1/

        # Restore a soft-deleted object
        POST /api/mymodel/1/restore/

        # Permanently delete
        DELETE /api/mymodel/1/hard_delete/
    """

    def perform_destroy(self, instance):
        """Soft delete the instance instead of hard deleting."""
        if hasattr(instance, 'delete'):
            # Soft delete
            instance.delete(user=self.request.user)
        else:
            # Fall back to hard delete if model doesn't support soft delete
            super().perform_destroy(instance)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted object.

        POST /api/mymodel/1/restore/
        """
        instance = self.get_object()

        if not hasattr(instance, 'restore'):
            return Response(
                {'error': 'Ce modèle ne supporte pas la restauration.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not instance.is_deleted:
            return Response(
                {'error': 'Cet objet n\'est pas supprimé.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.restore()

        # Log the restoration
        if hasattr(self, 'create_audit_log'):
            self.create_audit_log(
                action_type='restore',
                instance=instance,
                changes={'restored': True}
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='hard-delete')
    def hard_delete(self, request, pk=None):
        """
        Permanently delete an object.

        DELETE /api/mymodel/1/hard-delete/

        This action should be restricted to admins only.
        """
        instance = self.get_object()

        # Store object representation before deletion
        object_repr = str(instance)
        model_name = instance.__class__.__name__

        # Permanently delete
        if hasattr(instance, 'hard_delete'):
            instance.hard_delete()
        else:
            instance.delete()

        # Log the hard deletion
        if hasattr(self, 'create_audit_log'):
            self.create_audit_log(
                action_type=AuditLog.Action.DELETE,
                instance=None,
                changes={'hard_deleted': True},
                extra_data={
                    'model_name': model_name,
                    'object_repr': object_repr
                }
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class QuerySetFilterMixin:
    """
    Mixin to filter querysets based on user role.

    This ensures users only see data they're authorized to view:
    - ADMIN/DS: See everything
    - PEDAGOGICAL: See everything (read-only)
    - TEACHER: See only their students/classes
    - STUDENT: See only their own data

    Usage:
        class StudentViewSet(QuerySetFilterMixin, viewsets.ModelViewSet):
            queryset = Student.objects.all()
            filter_field = 'teacher'  # Field that links to the teacher

            def get_queryset_for_teacher(self, queryset):
                # Custom filtering for teachers
                return queryset.filter(teacher=self.request.user)
    """

    # Field name that links the model to the user (e.g., 'teacher', 'created_by')
    filter_field = None

    def get_queryset(self):
        """
        Filter queryset based on user role.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if not user or not user.is_authenticated:
            return queryset.none()

        # Admins and DS see everything
        if user.is_admin() or user.is_ds():
            return queryset

        # Pedagogical advisors see everything (read-only enforced by permissions)
        if user.is_pedagogical():
            return queryset

        # Teachers see only their data
        if user.is_teacher():
            return self.get_queryset_for_teacher(queryset)

        # Students see only their own data
        if hasattr(user, 'student'):
            return self.get_queryset_for_student(queryset)

        # Default: return empty queryset if no role matches
        return queryset.none()

    def get_queryset_for_teacher(self, queryset):
        """
        Filter queryset for teachers.

        Override this method for custom filtering logic.
        """
        if self.filter_field:
            return queryset.filter(**{self.filter_field: self.request.user})

        # If filter_field is not set, try common fields
        model = queryset.model
        if hasattr(model, 'teacher'):
            return queryset.filter(teacher=self.request.user)
        elif hasattr(model, 'created_by'):
            return queryset.filter(created_by=self.request.user)

        # If no suitable field found, return all (permissions will handle access)
        return queryset

    def get_queryset_for_student(self, queryset):
        """
        Filter queryset for students.

        Override this method for custom filtering logic.
        """
        user = self.request.user

        # Check if the model has a student field
        model = queryset.model
        if hasattr(model, 'student'):
            return queryset.filter(student=user.student)
        elif hasattr(model, 'user'):
            return queryset.filter(user=user)

        # Default: return empty queryset
        return queryset.none()


class ValidationMixin:
    """
    Mixin to add custom validation logic.

    Provides hooks for validating data before create/update operations.

    Usage:
        class MyViewSet(ValidationMixin, viewsets.ModelViewSet):
            def validate_create(self, request, serializer):
                # Custom validation logic
                if some_condition:
                    raise ValidationError("Error message")

            def validate_update(self, request, serializer):
                # Custom validation logic
                pass
    """

    def validate_create(self, request, serializer):
        """
        Hook for custom validation before creating an object.

        Override this in your viewset to add custom validation.
        Raise ValidationError if validation fails.
        """
        pass

    def validate_update(self, request, serializer):
        """
        Hook for custom validation before updating an object.

        Override this in your viewset to add custom validation.
        Raise ValidationError if validation fails.
        """
        pass

    def create(self, request, *args, **kwargs):
        """Override create to add custom validation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Run custom validation
        self.validate_create(request, serializer)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """Override update to add custom validation."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)

        # Run custom validation
        self.validate_update(request, serializer)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
