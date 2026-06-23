"""
Custom permission classes for SPAS.

This module defines granular permission classes for role-based access control:
- ADMIN: Full access to all resources
- TEACHER: Manages their own students and classes
- DS (Directeur des Études): Supervises all academic operations
- PEDAGOGICAL: Views and analyzes data across the system
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class that only allows administrators.

    Usage:
        permission_classes = [IsAuthenticated, IsAdmin]
    """
    message = "Seuls les administrateurs peuvent effectuer cette action."

    def has_permission(self, request, view):
        """Check if user is an admin."""
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin()
        )


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission class that allows teachers and administrators.

    Teachers can manage their own resources.
    Admins have full access.

    Usage:
        permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    """
    message = "Seuls les enseignants et administrateurs peuvent effectuer cette action."

    def has_permission(self, request, view):
        """Check if user is a teacher or admin."""
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_teacher() or request.user.is_admin())
        )


class IsDSOrAdmin(permissions.BasePermission):
    """
    Permission class that allows DS (Directeur des Études) and administrators.

    DS can supervise all academic operations.
    Admins have full access.

    Usage:
        permission_classes = [IsAuthenticated, IsDSOrAdmin]
    """
    message = "Seuls les directeurs des études et administrateurs peuvent effectuer cette action."

    def has_permission(self, request, view):
        """Check if user is DS or admin."""
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_ds() or request.user.is_admin())
        )


class IsPedagogicalOrAbove(permissions.BasePermission):
    """
    Permission class for pedagogical advisors and higher roles.

    Allows: PEDAGOGICAL, DS, ADMIN

    Usage:
        permission_classes = [IsAuthenticated, IsPedagogicalOrAbove]
    """
    message = "Accès réservé aux conseillers pédagogiques et supérieurs."

    def has_permission(self, request, view):
        """Check if user has pedagogical or higher role."""
        return (
            request.user
            and request.user.is_authenticated
            and request.user.has_elevated_permissions()
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Others can only read.

    Assumes the model has a 'created_by' or 'user' field.

    Usage:
        permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    """
    message = "Vous ne pouvez modifier que vos propres ressources."

    def has_object_permission(self, request, view, obj):
        """
        Read permissions are allowed for any authenticated user.
        Write permissions are only allowed to the owner.
        """
        # Read permissions are allowed for safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner or admin
        if request.user.is_admin():
            return True

        # Check if object has created_by or user field
        owner_field = getattr(obj, 'created_by', None) or getattr(obj, 'user', None)
        if owner_field:
            return owner_field == request.user

        # Check if object has teacher field
        teacher_field = getattr(obj, 'teacher', None)
        if teacher_field:
            return teacher_field == request.user

        return False


class IsStudentOwner(permissions.BasePermission):
    """
    Permission class for students to access their own data.

    Students can only view their own records.
    Staff can view all records.

    Note: This assumes there's a Student model linked to User.

    Usage:
        permission_classes = [IsAuthenticated, IsStudentOwner]
    """
    message = "Vous ne pouvez accéder qu'à vos propres données."

    def has_permission(self, request, view):
        """Allow all authenticated users to make requests."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Allow staff to view all objects.
        Allow students to view only their own objects.
        """
        # Staff members can access all objects
        if request.user.is_staff or request.user.has_elevated_permissions():
            return True

        # Check if the object has a student field linked to user
        student = getattr(obj, 'student', None)
        if student:
            # Check if the student is linked to the current user
            return hasattr(student, 'user') and student.user == request.user

        # Check if the object itself is the student and has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False


class CanManageStudents(permissions.BasePermission):
    """
    Permission class for users who can manage students.

    Allows: TEACHER (their own students), DS, ADMIN

    Usage:
        permission_classes = [IsAuthenticated, CanManageStudents]
    """
    message = "Vous n'avez pas la permission de gérer les étudiants."

    def has_permission(self, request, view):
        """Check if user can manage students."""
        if not (request.user and request.user.is_authenticated):
            return False

        # Admins and DS can manage all students
        if request.user.is_admin() or request.user.is_ds():
            return True

        # Teachers can manage students (filtered by object permissions)
        if request.user.is_teacher():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for student management.

        Teachers can only manage their own students.
        DS and Admins can manage all students.
        """
        # Admins and DS can manage all students
        if request.user.is_admin() or request.user.is_ds():
            return True

        # Teachers can only manage their own students
        if request.user.is_teacher():
            # Check if the student is assigned to this teacher
            teacher_field = getattr(obj, 'teacher', None)
            if teacher_field:
                return teacher_field == request.user

            # Check if the student is in one of the teacher's classes
            # This requires accessing the student's enrollments
            if hasattr(obj, 'enrollments'):
                teacher_classes = request.user.teaching_sessions.all()
                student_classes = obj.enrollments.values_list('session_id', flat=True)
                return teacher_classes.filter(id__in=student_classes).exists()

        return False


class CanViewPredictions(permissions.BasePermission):
    """
    Permission class for users who can view ML predictions.

    Allows: PEDAGOGICAL, DS, ADMIN
    Teachers can view predictions for their students only.

    Usage:
        permission_classes = [IsAuthenticated, CanViewPredictions]
    """
    message = "Vous n'avez pas la permission de voir les prédictions."

    def has_permission(self, request, view):
        """Check if user can view predictions."""
        if not (request.user and request.user.is_authenticated):
            return False

        # Elevated permissions can view all predictions
        if request.user.has_elevated_permissions():
            return True

        # Teachers can view predictions (filtered by object permissions)
        if request.user.is_teacher():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for viewing predictions.

        Teachers can only view predictions for their students.
        """
        # Elevated permissions can view all predictions
        if request.user.has_elevated_permissions():
            return True

        # Teachers can only view predictions for their students
        if request.user.is_teacher():
            # Get the student from the prediction
            student = getattr(obj, 'student', None)
            if student:
                # Check if the student is assigned to this teacher
                teacher_field = getattr(student, 'teacher', None)
                if teacher_field:
                    return teacher_field == request.user

                # Check if the student is in one of the teacher's classes
                if hasattr(student, 'enrollments'):
                    teacher_classes = request.user.teaching_sessions.all()
                    student_classes = student.enrollments.values_list('session_id', flat=True)
                    return teacher_classes.filter(id__in=student_classes).exists()

        return False


class CanManageAlerts(permissions.BasePermission):
    """
    Permission class for users who can manage alerts.

    Allows: TEACHER (their students), DS, ADMIN
    PEDAGOGICAL can view but not create/modify.

    Usage:
        permission_classes = [IsAuthenticated, CanManageAlerts]
    """
    message = "Vous n'avez pas la permission de gérer les alertes."

    def has_permission(self, request, view):
        """Check if user can manage alerts."""
        if not (request.user and request.user.is_authenticated):
            return False

        # Read-only for pedagogical advisors
        if request.user.is_pedagogical() and request.method in permissions.SAFE_METHODS:
            return True

        # Full access for DS and admins
        if request.user.is_ds() or request.user.is_admin():
            return True

        # Teachers can manage alerts for their students
        if request.user.is_teacher():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for alert management.

        Teachers can only manage alerts for their students.
        """
        # Admins and DS can manage all alerts
        if request.user.is_admin() or request.user.is_ds():
            return True

        # Pedagogical can view all alerts
        if request.user.is_pedagogical() and request.method in permissions.SAFE_METHODS:
            return True

        # Teachers can only manage alerts for their students
        if request.user.is_teacher():
            # Get the student from the alert
            student = getattr(obj, 'student', None)
            if student:
                # Check if the student is assigned to this teacher
                teacher_field = getattr(student, 'teacher', None)
                if teacher_field:
                    return teacher_field == request.user

                # Check if the student is in one of the teacher's classes
                if hasattr(student, 'enrollments'):
                    teacher_classes = request.user.teaching_sessions.all()
                    student_classes = student.enrollments.values_list('session_id', flat=True)
                    return teacher_classes.filter(id__in=student_classes).exists()

        return False


class CanRunMLPredictions(permissions.BasePermission):
    """
    Permission class for users who can run ML predictions.

    This is a resource-intensive operation, so it's restricted to:
    - DS (Directeur des Études)
    - ADMIN

    Usage:
        permission_classes = [IsAuthenticated, CanRunMLPredictions]
    """
    message = "Seuls les administrateurs et directeurs des études peuvent lancer des prédictions ML."

    def has_permission(self, request, view):
        """Check if user can run ML predictions."""
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_ds() or request.user.is_admin())
        )


def teacher_can_access_student(user, student):
    """
    Return True if the teacher `user` is authorised to access data for `student`.

    Checks in order:
    1. If the student model has a direct `teacher` FK, compare it to the user.
    2. Otherwise fall back to session/enrollment intersection.
    Fail-closed: returns False when neither relationship can be confirmed.
    """
    teacher_field = getattr(student, 'teacher', None)
    if teacher_field is not None:
        return teacher_field == user
    # Enrollment-based check (fail-closed: no enrollments → no access)
    teacher_classes = user.teaching_sessions.all()
    student_classes = student.enrollments.values_list('session_id', flat=True)
    return teacher_classes.filter(id__in=student_classes).exists()


class ReadOnlyPermission(permissions.BasePermission):
    """
    Permission class that allows read-only access.

    Useful for endpoints that should be viewable but not modifiable.

    Usage:
        permission_classes = [IsAuthenticated, ReadOnlyPermission]
    """
    message = "Cette ressource est en lecture seule."

    def has_permission(self, request, view):
        """Allow only safe methods."""
        return (
            request.user
            and request.user.is_authenticated
            and request.method in permissions.SAFE_METHODS
        )
