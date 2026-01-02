"""
Tests for core models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models import AuditLog, SoftDeleteModel

User = get_user_model()


class AuditLogTestCase(TestCase):
    """Tests for AuditLog model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.Role.TEACHER
        )

    def test_create_audit_log(self):
        """Test creating an audit log entry."""
        log = AuditLog.objects.create(
            user=self.user,
            action=AuditLog.Action.CREATE,
            model_name='Student',
            object_repr='John Doe',
            changes={'name': 'John Doe'},
            ip_address='192.168.1.1',
            endpoint='/api/students/',
            method='POST',
            status_code=201
        )

        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, AuditLog.Action.CREATE)
        self.assertEqual(log.model_name, 'Student')
        self.assertIsNotNone(log.timestamp)

    def test_log_action_method(self):
        """Test the log_action convenience method."""
        log = AuditLog.log_action(
            user=self.user,
            action=AuditLog.Action.UPDATE,
            changes={'status': 'active'},
            ip_address='192.168.1.1',
            endpoint='/api/students/1/',
            method='PATCH'
        )

        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, AuditLog.Action.UPDATE)
        self.assertEqual(log.changes, {'status': 'active'})

    def test_log_action_with_object(self):
        """Test logging an action with a content object."""
        log = AuditLog.log_action(
            user=self.user,
            action=AuditLog.Action.VIEW,
            content_object=self.user,
            ip_address='192.168.1.1'
        )

        self.assertEqual(log.content_object, self.user)
        self.assertEqual(log.model_name, 'User')
        self.assertEqual(log.object_repr, str(self.user))

    def test_audit_log_string_representation(self):
        """Test string representation of audit log."""
        log = AuditLog.log_action(
            user=self.user,
            action=AuditLog.Action.LOGIN,
            ip_address='192.168.1.1'
        )

        log_str = str(log)
        self.assertIn(self.user.get_full_name(), log_str)
        self.assertIn('Connexion', log_str)


class TestSoftDeleteModel(SoftDeleteModel):
    """Test model for soft deletion."""
    class Meta:
        app_label = 'core'


class SoftDeleteModelTestCase(TestCase):
    """Tests for SoftDeleteModel."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.Role.ADMIN
        )

    def test_soft_delete(self):
        """Test soft deletion."""
        # Note: This is a conceptual test since TestSoftDeleteModel
        # won't actually be in the database. In real usage, you would
        # test this with actual models that inherit from SoftDeleteModel.
        obj = TestSoftDeleteModel()
        obj.is_deleted = False

        # Soft delete
        obj.delete(user=self.user)

        self.assertTrue(obj.is_deleted)
        self.assertIsNotNone(obj.deleted_at)
        self.assertEqual(obj.deleted_by, self.user)

    def test_restore(self):
        """Test restoring a soft-deleted object."""
        obj = TestSoftDeleteModel()
        obj.is_deleted = True
        obj.deleted_at = timezone.now()
        obj.deleted_by = self.user

        # Restore
        obj.restore()

        self.assertFalse(obj.is_deleted)
        self.assertIsNone(obj.deleted_at)
        self.assertIsNone(obj.deleted_by)
