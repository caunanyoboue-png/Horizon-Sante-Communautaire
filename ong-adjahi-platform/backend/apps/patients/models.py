"""
Patient models for ONG ADJAHI Platform
"""

from django.db import models
from django.core.validators import RegexValidator
from apps.common.models import TimeStampedModel


class Patient(TimeStampedModel):
    """Patient model"""
    
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('UNKNOWN', 'Inconnu'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Célibataire'),
        ('MARRIED', 'Marié(e)'),
        ('DIVORCED', 'Divorcé(e)'),
        ('WIDOWED', 'Veuf/Veuve'),
    ]
    
    # Identification
    patient_id = models.CharField('ID Patient', max_length=20, unique=True, editable=False)
    first_name = models.CharField('Prénom', max_length=100)
    last_name = models.CharField('Nom', max_length=100)
    date_of_birth = models.DateField('Date de naissance')
    gender = models.CharField('Sexe', max_length=1, choices=GENDER_CHOICES)
    
    # Contact
    phone_regex = RegexValidator(
        regex=r'^\+?225?\d{10}$',
        message="Format: '+225XXXXXXXXXX'"
    )
    phone = models.CharField('Téléphone', validators=[phone_regex], max_length=15)
    email = models.EmailField('Email', blank=True)
    address = models.TextField('Adresse')
    city = models.CharField('Ville', max_length=100, default='Grand-Bassam')
    
    # Emergency contact
    emergency_contact_name = models.CharField('Contact d\'urgence (Nom)', max_length=200)
    emergency_contact_phone = models.CharField('Contact d\'urgence (Tel)', validators=[phone_regex], max_length=15)
    emergency_contact_relation = models.CharField('Relation', max_length=50)
    
    # Medical information
    blood_group = models.CharField('Groupe sanguin', max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    height = models.DecimalField('Taille (cm)', max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField('Poids (kg)', max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Social information
    marital_status = models.CharField('Statut marital', max_length=20, choices=MARITAL_STATUS_CHOICES, default='SINGLE')
    occupation = models.CharField('Profession', max_length=100, blank=True)
    
    # Registration
    registration_location = models.CharField('Lieu d\'enregistrement', max_length=50, default='Grand-Bassam')
    registered_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    
    # Status
    is_active = models.BooleanField('Actif', default=True)
    notes = models.TextField('Notes', blank=True)
    
    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.patient_id} - {self.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Generate unique patient ID: ADJ-YYYYMMDD-XXXX
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            last_patient = Patient.objects.filter(
                patient_id__startswith=f'ADJ-{today}'
            ).order_by('patient_id').last()
            
            if last_patient:
                last_number = int(last_patient.patient_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.patient_id = f'ADJ-{today}-{new_number:04d}'
        
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate patient age"""
        from django.utils import timezone
        today = timezone.now().date()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
            today.month == self.date_of_birth.month and today.day < self.date_of_birth.day
        ):
            age -= 1
        return age
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight available"""
        if self.height and self.weight:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 2)
        return None


class MedicalHistory(TimeStampedModel):
    """Patient medical history"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_histories')
    condition = models.CharField('Condition médicale', max_length=200)
    diagnosis_date = models.DateField('Date de diagnostic', null=True, blank=True)
    treatment = models.TextField('Traitement', blank=True)
    is_chronic = models.BooleanField('Chronique', default=False)
    is_active = models.BooleanField('Actif', default=True)
    notes = models.TextField('Notes', blank=True)
    recorded_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Antécédent médical'
        verbose_name_plural = 'Antécédents médicaux'
        ordering = ['-diagnosis_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.condition}"


class Allergy(TimeStampedModel):
    """Patient allergies"""
    
    SEVERITY_CHOICES = [
        ('MILD', 'Légère'),
        ('MODERATE', 'Modérée'),
        ('SEVERE', 'Sévère'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField('Allergène', max_length=200)
    reaction = models.TextField('Réaction')
    severity = models.CharField('Gravité', max_length=20, choices=SEVERITY_CHOICES)
    diagnosed_date = models.DateField('Date de diagnostic', null=True, blank=True)
    is_active = models.BooleanField('Actif', default=True)
    recorded_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Allergie'
        verbose_name_plural = 'Allergies'
        ordering = ['-severity', '-created_at']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.allergen}"


class Medication(TimeStampedModel):
    """Current patient medications"""
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField('Nom du médicament', max_length=200)
    dosage = models.CharField('Dosage', max_length=100)
    frequency = models.CharField('Fréquence', max_length=100)
    start_date = models.DateField('Date de début')
    end_date = models.DateField('Date de fin', null=True, blank=True)
    reason = models.TextField('Raison')
    is_active = models.BooleanField('Actif', default=True)
    prescribed_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Médicament'
        verbose_name_plural = 'Médicaments'
        ordering = ['-is_active', '-start_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.name}"
