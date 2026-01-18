"""
Models for Notifications
"""

from django.db import models
from apps.common.models import TimeStampedModel


class Notification(TimeStampedModel):
    """Generic notification model"""
    
    TYPE_CHOICES = [
        ('SMS', 'SMS'),
        ('EMAIL', 'Email'),
        ('PUSH', 'Push'),
        ('IN_APP', 'In-App'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('SENT', 'Envoyé'),
        ('FAILED', 'Échec'),
    ]
    
    recipient = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    recipient_email = models.EmailField('Email destinataire', blank=True)
    recipient_phone = models.CharField('Téléphone destinataire', max_length=15, blank=True)
    
    notification_type = models.CharField('Type', max_length=20, choices=TYPE_CHOICES)
    subject = models.CharField('Sujet', max_length=255)
    message = models.TextField('Message')
    
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField('Envoyé à', null=True, blank=True)
    error_message = models.TextField('Message d\'erreur', blank=True)
    
    # Metadata
    reference_type = models.CharField('Type de référence', max_length=50, blank=True)
    reference_id = models.CharField('ID de référence', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.subject} - {self.get_status_display()}"


class SMSLog(TimeStampedModel):
    """Log of SMS sent"""
    
    phone_number = models.CharField('Numéro de téléphone', max_length=15)
    message = models.TextField('Message')
    status = models.CharField('Statut', max_length=20)
    provider_response = models.TextField('Réponse du fournisseur', blank=True)
    cost = models.DecimalField('Coût', max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Journal SMS'
        verbose_name_plural = 'Journaux SMS'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS to {self.phone_number} - {self.status}"


class EmailLog(TimeStampedModel):
    """Log of emails sent"""
    
    to_email = models.EmailField('Destinataire')
    subject = models.CharField('Sujet', max_length=255)
    message = models.TextField('Message')
    status = models.CharField('Statut', max_length=20)
    error_message = models.TextField('Message d\'erreur', blank=True)
    
    class Meta:
        verbose_name = 'Journal Email'
        verbose_name_plural = 'Journaux Email'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email to {self.to_email} - {self.subject}"
