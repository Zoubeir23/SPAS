"""
Custom permission classes for SPAS.

These permissions control access based on user roles defined in the User model.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsTeacher(permissions.BasePermission):
    """
    Permission to only allow teacher users.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'teacher'
        )


class IsDataScientist(permissions.BasePermission):
    """
    Permission to only allow data scientist (DS) users.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ds'
        )


class IsPedagogical(permissions.BasePermission):
    """
    Permission to only allow pedagogical advisor users.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'pedagogical'
        )


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission to allow teachers or admins.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['teacher', 'admin']
        )


class IsTeacherOrAdminOrPedagogical(permissions.BasePermission):
    """
    Permission to allow teachers, admins, or pedagogical advisors.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['teacher', 'admin', 'pedagogical']
        )


class IsDataScientistOrAdmin(permissions.BasePermission):
    """
    Permission to allow data scientists or admins.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['ds', 'admin']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admins to edit it.

    The object must have a 'user' attribute or 'created_by' attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin can do anything
        if request.user.role == 'admin':
            return True

        # Check if object has user or created_by attribute
        owner = getattr(obj, 'user', None) or getattr(obj, 'created_by', None)
        return owner == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    Others can only read.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if object has user or created_by attribute
        owner = getattr(obj, 'user', None) or getattr(obj, 'created_by', None)
        return owner == request.user


class ReadOnly(permissions.BasePermission):
    """
    Permission to only allow read-only access.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class CanManageStudents(permissions.BasePermission):
    """
    Permission to manage students (teachers, admins, pedagogical).
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.role in ['teacher', 'admin', 'pedagogical'] or
                request.user.has_perm('users.can_manage_students')
            )
        )


class CanManageGrades(permissions.BasePermission):
    """
    Permission to manage grades (teachers and admins).
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.role in ['teacher', 'admin'] or
                request.user.has_perm('users.can_manage_grades')
            )
        )


class CanManageAttendance(permissions.BasePermission):
    """
    Permission to manage attendance (teachers and admins).
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.role in ['teacher', 'admin'] or
                request.user.has_perm('users.can_manage_attendance')
            )
        )


class CanRunMLPredictions(permissions.BasePermission):
    """
    Permission to run ML predictions (data scientists and admins).
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.role in ['ds', 'admin'] or
                request.user.has_perm('users.can_run_ml_predictions')
            )
        )


class CanViewPredictions(permissions.BasePermission):
    """
    Permission to view ML predictions (all authenticated users).
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.has_perm('users.can_view_predictions') or
                request.user.role in ['teacher', 'admin', 'ds', 'pedagogical']
            )
        )


class CanViewAnalytics(permissions.BasePermission):
    """
    Permission to view analytics dashboard.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.has_perm('users.can_view_analytics') or
                request.user.role in ['admin', 'ds', 'pedagogical']
            )
        )
