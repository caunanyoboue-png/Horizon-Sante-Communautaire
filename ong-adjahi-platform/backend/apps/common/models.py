"""
Common models for ONG ADJAHI Platform
"""

from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    
    created_at = models.DateTimeField('Date de création', auto_now_add=True)
    updated_at = models.DateTimeField('Date de modification', auto_now=True)
    
    class Meta:
        abstract = True


class AuditLog(TimeStampedModel):
    """Audit log for tracking user actions"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('VIEW', 'Consultation'),
        ('EXPORT', 'Export'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='Utilisateur'
    )
    action = models.CharField('Action', max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField('Modèle', max_length=100)
    object_id = models.CharField('ID Objet', max_length=100, blank=True)
    description = models.TextField('Description')
    ip_address = models.GenericIPAddressField('Adresse IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    
    class Meta:
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journaux d\'audit'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['model_name']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.model_name}"
