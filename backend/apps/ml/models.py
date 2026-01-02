"""
Machine Learning models for SPAS.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class MLModel(models.Model):
    """ML model metadata - Represents a trained machine learning model."""

    class Status(models.TextChoices):
        """ML model status choices."""
        ACTIVE = 'active', _('Actif')
        INACTIVE = 'inactive', _('Inactif')
        TRAINING = 'training', _('En Formation')

    # Model Information
    name = models.CharField(_('name'), max_length=200)
    version = models.CharField(_('version'), max_length=50, db_index=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.INACTIVE,
        db_index=True
    )

    # Model Metrics (0-100 scale)
    accuracy = models.DecimalField(
        _('accuracy'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Model accuracy (0-100)')
    )
    precision = models.DecimalField(
        _('precision'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Model precision (0-100)')
    )
    recall = models.DecimalField(
        _('recall'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Model recall (0-100)')
    )
    f1_score = models.DecimalField(
        _('F1 score'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Model F1 score (0-100)')
    )

    # Training Information
    trained_at = models.DateTimeField(_('trained at'))
    training_data_size = models.IntegerField(
        _('training data size'),
        validators=[MinValueValidator(0)],
        help_text=_('Number of samples used for training')
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'ml_models'
        verbose_name = _('ML model')
        verbose_name_plural = _('ML models')
        ordering = ['-trained_at', '-created_at']
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['status']),
            models.Index(fields=['-trained_at']),
        ]
        unique_together = [['name', 'version']]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.status})"

    def activate(self):
        """Activate this model and deactivate all others with the same name."""
        # Deactivate all other models with same name
        MLModel.objects.filter(name=self.name, status=self.Status.ACTIVE).update(
            status=self.Status.INACTIVE
        )
        # Activate this model
        self.status = self.Status.ACTIVE
        self.save(update_fields=['status', 'updated_at'])

    def is_active(self):
        """Check if this model is currently active."""
        return self.status == self.Status.ACTIVE

    @property
    def average_score(self):
        """Calculate average of all metrics."""
        return (self.accuracy + self.precision + self.recall + self.f1_score) / 4


class TrainingJob(models.Model):
    """Training job - Tracks ML model training process."""

    class Status(models.TextChoices):
        """Training job status choices."""
        PENDING = 'pending', _('En attente')
        RUNNING = 'running', _('En cours')
        COMPLETED = 'completed', _('Terminé')
        FAILED = 'failed', _('Échoué')
        CANCELLED = 'cancelled', _('Annulé')

    class JobType(models.TextChoices):
        """Training job type choices."""
        TRAIN = 'train', _('Entraînement')
        RETRAIN = 'retrain', _('Ré-entraînement')
        FINE_TUNE = 'fine_tune', _('Ajustement fin')

    # Job Information
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    job_type = models.CharField(
        _('job type'),
        max_length=20,
        choices=JobType.choices,
        default=JobType.TRAIN
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    # Training Configuration
    algorithm = models.CharField(
        _('algorithm'),
        max_length=50,
        default='random_forest',
        help_text=_('ML algorithm: random_forest, gradient_boosting, logistic_regression')
    )
    hyperparameters = models.JSONField(
        _('hyperparameters'),
        default=dict,
        blank=True,
        help_text=_('JSON object with hyperparameters')
    )
    features = models.JSONField(
        _('features'),
        default=list,
        blank=True,
        help_text=_('List of feature names to use')
    )

    # Progress Tracking
    progress = models.IntegerField(
        _('progress'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Training progress (0-100)')
    )
    current_step = models.CharField(
        _('current step'),
        max_length=100,
        blank=True,
        null=True
    )
    logs = models.TextField(_('logs'), blank=True, null=True)

    # Results
    resulting_model = models.ForeignKey(
        MLModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_jobs',
        verbose_name=_('resulting model')
    )
    error_message = models.TextField(_('error message'), blank=True, null=True)

    # Timing
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    # User who started the job
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='training_jobs',
        verbose_name=_('created by')
    )

    class Meta:
        db_table = 'training_jobs'
        verbose_name = _('Training job')
        verbose_name_plural = _('Training jobs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def duration(self):
        """Calculate training duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def start(self):
        """Mark job as started."""
        from django.utils import timezone
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.progress = 0
        self.save(update_fields=['status', 'started_at', 'progress', 'updated_at'])

    def complete(self, model=None):
        """Mark job as completed."""
        from django.utils import timezone
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.progress = 100
        self.resulting_model = model
        self.save(update_fields=['status', 'completed_at', 'progress', 'resulting_model', 'updated_at'])

    def fail(self, error_message):
        """Mark job as failed."""
        from django.utils import timezone
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=['status', 'completed_at', 'error_message', 'updated_at'])

    def update_progress(self, progress, step=None, logs=None):
        """Update job progress."""
        self.progress = min(progress, 100)
        if step:
            self.current_step = step
        if logs:
            self.logs = (self.logs or '') + '\n' + logs
        self.save(update_fields=['progress', 'current_step', 'logs', 'updated_at'])
