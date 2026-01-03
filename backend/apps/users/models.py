"""
User models for SPAS.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for SPAS."""

    class Role(models.TextChoices):
        """User role choices."""
        ADMIN = 'admin', _('Administrateur')
        TEACHER = 'teacher', _('Enseignant')
        DS = 'ds', _('Directeur des Études')
        PEDAGOGICAL = 'pedagogical', _('Conseiller Pédagogique')

    # Remove default username field - use email as username
    username = None

    # User Information
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.TEACHER,
        db_index=True
    )
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text=_('User profile picture')
    )

    # Metadata
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
        permissions = [
            ('can_view_analytics', 'Can view analytics dashboard'),
            ('can_manage_students', 'Can manage students'),
            ('can_manage_programs', 'Can manage programs'),
            ('can_manage_grades', 'Can manage grades'),
            ('can_manage_attendance', 'Can manage attendance'),
            ('can_run_ml_predictions', 'Can run ML predictions'),
            ('can_view_predictions', 'Can view ML predictions'),
            ('can_manage_alerts', 'Can manage alerts'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def is_admin(self):
        """Check if user is admin."""
        return self.role == self.Role.ADMIN

    def is_teacher(self):
        """Check if user is teacher."""
        return self.role == self.Role.TEACHER

    def is_ds(self):
        """Check if user is DS (Directeur des Études)."""
        return self.role == self.Role.DS

    def is_pedagogical(self):
        """Check if user is pedagogical advisor."""
        return self.role == self.Role.PEDAGOGICAL

    def has_elevated_permissions(self):
        """Check if user has elevated permissions (admin, DS, or pedagogical)."""
        return self.role in [self.Role.ADMIN, self.Role.DS, self.Role.PEDAGOGICAL]
