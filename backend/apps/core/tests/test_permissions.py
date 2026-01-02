"""
Tests for custom permission classes.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.core.permissions import (
    IsAdmin,
    IsTeacherOrAdmin,
    IsDSOrAdmin,
    IsPedagogicalOrAbove,
    IsOwnerOrReadOnly,
    CanManageStudents,
    CanViewPredictions,
    CanManageAlerts,
    CanRunMLPredictions,
    ReadOnlyPermission,
)

User = get_user_model()


class PermissionTestCase(TestCase):
    """Base test case for permission tests."""

    def setUp(self):
        """Set up test users with different roles."""
        self.factory = APIRequestFactory()

        # Create users with different roles
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN
        )

        self.ds = User.objects.create_user(
            email='ds@test.com',
            password='testpass123',
            first_name='DS',
            last_name='User',
            role=User.Role.DS
        )

        self.pedagogical = User.objects.create_user(
            email='pedagogical@test.com',
            password='testpass123',
            first_name='Pedagogical',
            last_name='User',
            role=User.Role.PEDAGOGICAL
        )

        self.teacher = User.objects.create_user(
            email='teacher@test.com',
            password='testpass123',
            first_name='Teacher',
            last_name='User',
            role=User.Role.TEACHER
        )

        # Create a mock view
        self.view = APIView()


class IsAdminPermissionTest(PermissionTestCase):
    """Tests for IsAdmin permission."""

    def test_admin_has_permission(self):
        """Test that admin users have permission."""
        permission = IsAdmin()
        request = self.factory.get('/')
        request.user = self.admin

        self.assertTrue(permission.has_permission(request, self.view))

    def test_non_admin_no_permission(self):
        """Test that non-admin users don't have permission."""
        permission = IsAdmin()

        for user in [self.ds, self.pedagogical, self.teacher]:
            request = self.factory.get('/')
            request.user = user
            self.assertFalse(permission.has_permission(request, self.view))


class IsTeacherOrAdminPermissionTest(PermissionTestCase):
    """Tests for IsTeacherOrAdmin permission."""

    def test_teacher_has_permission(self):
        """Test that teachers have permission."""
        permission = IsTeacherOrAdmin()
        request = self.factory.get('/')
        request.user = self.teacher

        self.assertTrue(permission.has_permission(request, self.view))

    def test_admin_has_permission(self):
        """Test that admins have permission."""
        permission = IsTeacherOrAdmin()
        request = self.factory.get('/')
        request.user = self.admin

        self.assertTrue(permission.has_permission(request, self.view))

    def test_non_teacher_no_permission(self):
        """Test that non-teachers/admins don't have permission."""
        permission = IsTeacherOrAdmin()

        for user in [self.ds, self.pedagogical]:
            request = self.factory.get('/')
            request.user = user
            self.assertFalse(permission.has_permission(request, self.view))


class IsDSOrAdminPermissionTest(PermissionTestCase):
    """Tests for IsDSOrAdmin permission."""

    def test_ds_has_permission(self):
        """Test that DS users have permission."""
        permission = IsDSOrAdmin()
        request = self.factory.get('/')
        request.user = self.ds

        self.assertTrue(permission.has_permission(request, self.view))

    def test_admin_has_permission(self):
        """Test that admins have permission."""
        permission = IsDSOrAdmin()
        request = self.factory.get('/')
        request.user = self.admin

        self.assertTrue(permission.has_permission(request, self.view))

    def test_non_ds_no_permission(self):
        """Test that non-DS/admins don't have permission."""
        permission = IsDSOrAdmin()

        for user in [self.pedagogical, self.teacher]:
            request = self.factory.get('/')
            request.user = user
            self.assertFalse(permission.has_permission(request, self.view))


class IsPedagogicalOrAbovePermissionTest(PermissionTestCase):
    """Tests for IsPedagogicalOrAbove permission."""

    def test_elevated_roles_have_permission(self):
        """Test that pedagogical, DS, and admin have permission."""
        permission = IsPedagogicalOrAbove()

        for user in [self.pedagogical, self.ds, self.admin]:
            request = self.factory.get('/')
            request.user = user
            self.assertTrue(
                permission.has_permission(request, self.view),
                f"{user.role} should have permission"
            )

    def test_teacher_no_permission(self):
        """Test that teachers don't have permission."""
        permission = IsPedagogicalOrAbove()
        request = self.factory.get('/')
        request.user = self.teacher

        self.assertFalse(permission.has_permission(request, self.view))


class IsOwnerOrReadOnlyPermissionTest(PermissionTestCase):
    """Tests for IsOwnerOrReadOnly permission."""

    def setUp(self):
        super().setUp()
        self.permission = IsOwnerOrReadOnly()

        # Create a mock object with created_by field
        class MockObject:
            def __init__(self, created_by):
                self.created_by = created_by

        self.mock_obj = MockObject(created_by=self.teacher)

    def test_read_permission_for_all(self):
        """Test that all authenticated users can read."""
        for user in [self.admin, self.ds, self.pedagogical, self.teacher]:
            request = self.factory.get('/')
            request.user = user
            self.assertTrue(
                self.permission.has_object_permission(request, self.view, self.mock_obj)
            )

    def test_write_permission_for_owner(self):
        """Test that owners can write."""
        request = self.factory.post('/')
        request.user = self.teacher
        self.assertTrue(
            self.permission.has_object_permission(request, self.view, self.mock_obj)
        )

    def test_write_permission_for_admin(self):
        """Test that admins can write."""
        request = self.factory.post('/')
        request.user = self.admin
        self.assertTrue(
            self.permission.has_object_permission(request, self.view, self.mock_obj)
        )

    def test_no_write_permission_for_non_owner(self):
        """Test that non-owners can't write."""
        request = self.factory.post('/')
        request.user = self.pedagogical
        self.assertFalse(
            self.permission.has_object_permission(request, self.view, self.mock_obj)
        )


class CanManageStudentsPermissionTest(PermissionTestCase):
    """Tests for CanManageStudents permission."""

    def test_admin_can_manage(self):
        """Test that admins can manage students."""
        permission = CanManageStudents()
        request = self.factory.get('/')
        request.user = self.admin

        self.assertTrue(permission.has_permission(request, self.view))

    def test_ds_can_manage(self):
        """Test that DS can manage students."""
        permission = CanManageStudents()
        request = self.factory.get('/')
        request.user = self.ds

        self.assertTrue(permission.has_permission(request, self.view))

    def test_teacher_can_manage(self):
        """Test that teachers can manage students."""
        permission = CanManageStudents()
        request = self.factory.get('/')
        request.user = self.teacher

        self.assertTrue(permission.has_permission(request, self.view))

    def test_pedagogical_cannot_manage(self):
        """Test that pedagogical advisors can't manage students."""
        permission = CanManageStudents()
        request = self.factory.get('/')
        request.user = self.pedagogical

        self.assertFalse(permission.has_permission(request, self.view))


class CanViewPredictionsPermissionTest(PermissionTestCase):
    """Tests for CanViewPredictions permission."""

    def test_elevated_roles_can_view(self):
        """Test that pedagogical, DS, and admin can view predictions."""
        permission = CanViewPredictions()

        for user in [self.pedagogical, self.ds, self.admin]:
            request = self.factory.get('/')
            request.user = user
            self.assertTrue(
                permission.has_permission(request, self.view),
                f"{user.role} should be able to view predictions"
            )

    def test_teacher_can_view(self):
        """Test that teachers can view predictions."""
        permission = CanViewPredictions()
        request = self.factory.get('/')
        request.user = self.teacher

        self.assertTrue(permission.has_permission(request, self.view))


class CanManageAlertsPermissionTest(PermissionTestCase):
    """Tests for CanManageAlerts permission."""

    def test_admin_can_manage(self):
        """Test that admins can manage alerts."""
        permission = CanManageAlerts()
        request = self.factory.post('/')
        request.user = self.admin

        self.assertTrue(permission.has_permission(request, self.view))

    def test_ds_can_manage(self):
        """Test that DS can manage alerts."""
        permission = CanManageAlerts()
        request = self.factory.post('/')
        request.user = self.ds

        self.assertTrue(permission.has_permission(request, self.view))

    def test_teacher_can_manage(self):
        """Test that teachers can manage alerts."""
        permission = CanManageAlerts()
        request = self.factory.post('/')
        request.user = self.teacher

        self.assertTrue(permission.has_permission(request, self.view))

    def test_pedagogical_can_read_only(self):
        """Test that pedagogical advisors can only read."""
        permission = CanManageAlerts()

        # Can read
        read_request = self.factory.get('/')
        read_request.user = self.pedagogical
        self.assertTrue(permission.has_permission(read_request, self.view))

        # Cannot write
        write_request = self.factory.post('/')
        write_request.user = self.pedagogical
        self.assertFalse(permission.has_permission(write_request, self.view))


class CanRunMLPredictionsPermissionTest(PermissionTestCase):
    """Tests for CanRunMLPredictions permission."""

    def test_admin_can_run(self):
        """Test that admins can run ML predictions."""
        permission = CanRunMLPredictions()
        request = self.factory.post('/')
        request.user = self.admin

        self.assertTrue(permission.has_permission(request, self.view))

    def test_ds_can_run(self):
        """Test that DS can run ML predictions."""
        permission = CanRunMLPredictions()
        request = self.factory.post('/')
        request.user = self.ds

        self.assertTrue(permission.has_permission(request, self.view))

    def test_others_cannot_run(self):
        """Test that other roles can't run ML predictions."""
        permission = CanRunMLPredictions()

        for user in [self.pedagogical, self.teacher]:
            request = self.factory.post('/')
            request.user = user
            self.assertFalse(
                permission.has_permission(request, self.view),
                f"{user.role} should not be able to run ML predictions"
            )


class ReadOnlyPermissionTest(PermissionTestCase):
    """Tests for ReadOnlyPermission."""

    def test_read_allowed(self):
        """Test that read operations are allowed."""
        permission = ReadOnlyPermission()

        for method in ['get', 'head', 'options']:
            request = getattr(self.factory, method)('/')
            request.user = self.teacher
            self.assertTrue(
                permission.has_permission(request, self.view),
                f"{method.upper()} should be allowed"
            )

    def test_write_not_allowed(self):
        """Test that write operations are not allowed."""
        permission = ReadOnlyPermission()

        for method in ['post', 'put', 'patch', 'delete']:
            request = getattr(self.factory, method)('/')
            request.user = self.teacher
            self.assertFalse(
                permission.has_permission(request, self.view),
                f"{method.upper()} should not be allowed"
            )
