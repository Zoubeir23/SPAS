"""
Core models for SPAS.

This module contains shared models used across the application:
- AuditLog: Tracks important actions and changes for security and compliance
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    Audit log model for tracking all important actions in the system.

    This model creates an audit trail for compliance and security:
    - Who performed the action
    - What action was performed
    - When it was performed
    - What object was affected
    - What changes were made
    - From which IP address

    Usage:
        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.CREATE,
            content_object=student,
            changes={'name': 'John Doe', 'email': 'john@example.com'},
            ip_address=get_client_ip(request)
        )
    """

    class Action(models.TextChoices):
        """Possible actions that can be audited."""
        CREATE = 'create', _('Création')
        UPDATE = 'update', _('Modification')
        DELETE = 'delete', _('Suppression')
        VIEW = 'view', _('Consultation')
        LOGIN = 'login', _('Connexion')
        LOGOUT = 'logout', _('Déconnexion')
        EXPORT = 'export', _('Exportation')
        IMPORT = 'import', _('Importation')
        ML_PREDICTION = 'ml_prediction', _('Prédiction ML')
        ALERT_CREATED = 'alert_created', _('Alerte créée')
        ALERT_RESOLVED = 'alert_resolved', _('Alerte résolue')
        PERMISSION_DENIED = 'permission_denied', _('Permission refusée')
        ERROR = 'error', _('Erreur')

    # Who performed the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('utilisateur'),
        help_text=_("L'utilisateur qui a effectué l'action")
    )

    # What action was performed
    action = models.CharField(
        _('action'),
        max_length=50,
        choices=Action.choices,
        db_index=True,
        help_text=_("Le type d'action effectuée")
    )

    # What object was affected (generic foreign key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('type de contenu')
    )
    object_id = models.PositiveIntegerField(
        _('ID de l\'objet'),
        null=True,
        blank=True,
        db_index=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional details
    model_name = models.CharField(
        _('nom du modèle'),
        max_length=100,
        db_index=True,
        help_text=_("Le nom du modèle affecté")
    )
    object_repr = models.CharField(
        _('représentation de l\'objet'),
        max_length=200,
        blank=True,
        help_text=_("Représentation textuelle de l'objet au moment de l'action")
    )

    # Changes made (JSON field)
    changes = models.JSONField(
        _('changements'),
        null=True,
        blank=True,
        help_text=_("Détails des changements effectués (format JSON)")
    )

    # Metadata
    ip_address = models.GenericIPAddressField(
        _('adresse IP'),
        null=True,
        blank=True,
        help_text=_("L'adresse IP de l'utilisateur")
    )
    user_agent = models.CharField(
        _('user agent'),
        max_length=500,
        blank=True,
        help_text=_("Le user agent du navigateur")
    )
    timestamp = models.DateTimeField(
        _('horodatage'),
        auto_now_add=True,
        db_index=True,
        help_text=_("Quand l'action a été effectuée")
    )

    # Additional context
    endpoint = models.CharField(
        _('endpoint'),
        max_length=200,
        blank=True,
        help_text=_("L'endpoint API appelé")
    )
    method = models.CharField(
        _('méthode HTTP'),
        max_length=10,
        blank=True,
        help_text=_("La méthode HTTP utilisée (GET, POST, etc.)")
    )
    status_code = models.PositiveIntegerField(
        _('code de statut'),
        null=True,
        blank=True,
        help_text=_("Le code de statut HTTP de la réponse")
    )

    # Extra information
    extra_data = models.JSONField(
        _('données supplémentaires'),
        null=True,
        blank=True,
        help_text=_("Informations supplémentaires (format JSON)")
    )

    class Meta:
        db_table = 'audit_logs'
        verbose_name = _('journal d\'audit')
        verbose_name_plural = _('journaux d\'audit')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['model_name', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]

    def __str__(self):
        user_str = self.user.get_full_name() if self.user else 'Système'
        return f"{user_str} - {self.get_action_display()} - {self.model_name} - {self.timestamp}"

    @classmethod
    def log_action(cls, user, action, content_object=None, changes=None,
                   ip_address=None, user_agent=None, endpoint=None,
                   method=None, status_code=None, extra_data=None):
        """
        Convenience method to create an audit log entry.

        Args:
            user: The user performing the action
            action: The action being performed (use Action enum)
            content_object: The object being affected (optional)
            changes: Dictionary of changes made (optional)
            ip_address: IP address of the user (optional)
            user_agent: User agent string (optional)
            endpoint: API endpoint called (optional)
            method: HTTP method (optional)
            status_code: HTTP status code (optional)
            extra_data: Additional data (optional)

        Returns:
            AuditLog instance
        """
        log_data = {
            'user': user,
            'action': action,
            'changes': changes,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'extra_data': extra_data,
        }

        if content_object:
            log_data['content_object'] = content_object
            log_data['model_name'] = content_object.__class__.__name__
            log_data['object_repr'] = str(content_object)
        else:
            log_data['model_name'] = 'System'

        return cls.objects.create(**log_data)


class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom queryset that filters out soft-deleted objects by default.
    """

    def active(self):
        """Return only active (not deleted) objects."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only deleted objects."""
        return self.filter(is_deleted=True)

    def hard_delete(self):
        """Permanently delete objects."""
        return super().delete()


class SoftDeleteManager(models.Manager):
    """
    Manager that uses SoftDeleteQuerySet.
    """

    def get_queryset(self):
        """Override get_queryset to use custom queryset."""
        return SoftDeleteQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        """Get all objects including deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Get only deleted objects."""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft deletion.

    Instead of permanently deleting records, this marks them as deleted.
    This is useful for maintaining data integrity and audit trails.

    Usage:
        class MyModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            ...

        # Soft delete
        obj.delete()  # Sets is_deleted=True

        # Hard delete
        obj.hard_delete()  # Permanently removes from database

        # Query active objects
        MyModel.objects.all()  # Only non-deleted

        # Query all objects
        MyModel.objects.all_with_deleted()

        # Query deleted objects
        MyModel.objects.deleted_only()
    """

    is_deleted = models.BooleanField(
        _('supprimé'),
        default=False,
        db_index=True,
        help_text=_("Indique si l'objet a été supprimé")
    )
    deleted_at = models.DateTimeField(
        _('supprimé le'),
        null=True,
        blank=True,
        help_text=_("Date et heure de la suppression")
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name=_('supprimé par'),
        help_text=_("L'utilisateur qui a supprimé l'objet")
    )

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, user=None):
        """Soft delete the object."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
