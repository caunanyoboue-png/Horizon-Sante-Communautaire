"""
Custom User Model for ONG ADJAHI Platform
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from apps.common.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    """Custom User model for ONG ADJAHI"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('DOCTOR', 'Médecin'),
        ('MIDWIFE', 'Sage-femme'),
        ('COMMUNITY_AGENT', 'Agent Communautaire'),
        ('PSYCHOLOGIST', 'Psychologue'),
        ('NURSE', 'Infirmier/Infirmière'),
        ('PATIENT', 'Patient'),
    ]
    
    LOCATION_CHOICES = [
        ('GRAND_BASSAM', 'Grand-Bassam'),
        ('BONOUA', 'Bonoua'),
        ('BOTH', 'Les deux sites'),
    ]
    
    username = None  # Remove username field
    email = models.EmailField('Email', unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?225?\d{10}$',
        message="Format: '+225XXXXXXXXXX' ou '0XXXXXXXXX'"
    )
    phone = models.CharField('Téléphone', validators=[phone_regex], max_length=15, unique=True)
    
    first_name = models.CharField('Prénom', max_length=150)
    last_name = models.CharField('Nom', max_length=150)
    role = models.CharField('Rôle', max_length=20, choices=ROLE_CHOICES)
    location = models.CharField('Localisation', max_length=20, choices=LOCATION_CHOICES, default='GRAND_BASSAM')
    
    # Professional information
    specialization = models.CharField('Spécialisation', max_length=100, blank=True)
    license_number = models.CharField('Numéro de licence', max_length=50, blank=True)
    
    # 2FA
    is_2fa_enabled = models.BooleanField('2FA activé', default=False)
    
    # Status
    is_active = models.BooleanField('Actif', default=True)
    last_login_ip = models.GenericIPAddressField('Dernière IP', null=True, blank=True)
    
    # Profile
    avatar = models.ImageField('Photo de profil', upload_to='avatars/', null=True, blank=True)
    bio = models.TextField('Biographie', blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'role']
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_medical_staff(self):
        """Check if user is medical staff"""
        return self.role in ['DOCTOR', 'MIDWIFE', 'NURSE', 'PSYCHOLOGIST']
    
    @property
    def can_manage_patients(self):
        """Check if user can manage patients"""
        return self.role in ['ADMIN', 'DOCTOR', 'MIDWIFE', 'NURSE']
    
    @property
    def can_create_cpn(self):
        """Check if user can create CPN records"""
        return self.role in ['MIDWIFE', 'DOCTOR']


class LoginHistory(TimeStampedModel):
    """Track user login history for security"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField('Adresse IP')
    user_agent = models.TextField('User Agent')
    success = models.BooleanField('Succès', default=True)
    failure_reason = models.CharField('Raison de l\'échec', max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Historique de connexion'
        verbose_name_plural = 'Historiques de connexion'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Succès" if self.success else f"Échec: {self.failure_reason}"
        return f"{self.user.email} - {self.ip_address} - {status}"
