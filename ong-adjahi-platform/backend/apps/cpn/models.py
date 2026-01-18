"""
CPN (Consultation Prénatale) models for ONG ADJAHI Platform
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel
from datetime import timedelta


class Pregnancy(TimeStampedModel):
    """Pregnancy tracking for female patients"""
    
    STATUS_CHOICES = [
        ('ONGOING', 'En cours'),
        ('COMPLETED', 'Terminée'),
        ('MISCARRIAGE', 'Fausse couche'),
        ('ABORTION', 'IVG'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Élevé'),
    ]
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='pregnancies')
    pregnancy_number = models.PositiveIntegerField('Numéro de grossesse', help_text='G (Gestité)')
    parity = models.PositiveIntegerField('Parité', help_text='P (nombre d\'accouchements)')
    
    # Dates
    last_menstrual_period = models.DateField('Date des dernières règles (DDR)')
    expected_delivery_date = models.DateField('Date présumée d\'accouchement (DPA)', editable=False)
    actual_delivery_date = models.DateField('Date d\'accouchement réelle', null=True, blank=True)
    
    # Status
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='ONGOING')
    risk_level = models.CharField('Niveau de risque', max_length=20, choices=RISK_LEVEL_CHOICES, default='LOW')
    
    # Medical info
    blood_group_verified = models.BooleanField('Groupe sanguin vérifié', default=False)
    rh_factor = models.CharField('Facteur Rhésus', max_length=10, blank=True)
    
    # Risk factors
    has_diabetes = models.BooleanField('Diabète', default=False)
    has_hypertension = models.BooleanField('Hypertension', default=False)
    has_anemia = models.BooleanField('Anémie', default=False)
    other_risks = models.TextField('Autres risques', blank=True)
    
    # Staff
    assigned_midwife = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_pregnancies',
        limit_choices_to={'role': 'MIDWIFE'}
    )
    
    notes = models.TextField('Notes', blank=True)
    
    class Meta:
        verbose_name = 'Grossesse'
        verbose_name_plural = 'Grossesses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['expected_delivery_date']),
            models.Index(fields=['risk_level']),
        ]
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - G{self.pregnancy_number}P{self.parity}"
    
    def save(self, *args, **kwargs):
        # Calculate expected delivery date (280 days from LMP)
        if not self.expected_delivery_date:
            self.expected_delivery_date = self.last_menstrual_period + timedelta(days=280)
        super().save(*args, **kwargs)
    
    @property
    def gestational_age_weeks(self):
        """Calculate current gestational age in weeks"""
        if self.status != 'ONGOING':
            return None
        
        from django.utils import timezone
        today = timezone.now().date()
        days_pregnant = (today - self.last_menstrual_period).days
        return days_pregnant // 7
    
    @property
    def gestational_age_display(self):
        """Display gestational age in weeks and days"""
        if self.status != 'ONGOING':
            return 'Terminée'
        
        from django.utils import timezone
        today = timezone.now().date()
        days_pregnant = (today - self.last_menstrual_period).days
        weeks = days_pregnant // 7
        days = days_pregnant % 7
        return f"{weeks} SA + {days} jours"
    
    @property
    def trimester(self):
        """Get current trimester"""
        weeks = self.gestational_age_weeks
        if weeks is None:
            return None
        if weeks < 14:
            return 1
        elif weeks < 28:
            return 2
        else:
            return 3


class CPNConsultation(TimeStampedModel):
    """CPN Consultation (CPN1 to CPN4+)"""
    
    CPN_TYPE_CHOICES = [
        ('CPN1', 'CPN1 (avant 16 SA)'),
        ('CPN2', 'CPN2 (24-28 SA)'),
        ('CPN3', 'CPN3 (30-32 SA)'),
        ('CPN4', 'CPN4 (36-38 SA)'),
        ('CPN_EXTRA', 'CPN supplémentaire'),
    ]
    
    pregnancy = models.ForeignKey(Pregnancy, on_delete=models.CASCADE, related_name='cpn_consultations')
    cpn_type = models.CharField('Type de CPN', max_length=20, choices=CPN_TYPE_CHOICES)
    consultation_date = models.DateField('Date de consultation')
    gestational_age_weeks = models.PositiveIntegerField('Âge gestationnel (SA)', validators=[MaxValueValidator(42)])
    
    # Vital signs
    weight = models.DecimalField('Poids (kg)', max_digits=5, decimal_places=2)
    blood_pressure_systolic = models.PositiveIntegerField('Tension systolique', validators=[MaxValueValidator(300)])
    blood_pressure_diastolic = models.PositiveIntegerField('Tension diastolique', validators=[MaxValueValidator(200)])
    temperature = models.DecimalField('Température (°C)', max_digits=4, decimal_places=1, null=True, blank=True)
    
    # Uterine measurements
    fundal_height = models.DecimalField('Hauteur utérine (cm)', max_digits=4, decimal_places=1, null=True, blank=True)
    fetal_heart_rate = models.PositiveIntegerField('Fréquence cardiaque fœtale (bpm)', null=True, blank=True)
    
    # Lab tests
    hemoglobin = models.DecimalField('Hémoglobine (g/dL)', max_digits=4, decimal_places=1, null=True, blank=True)
    glucose = models.DecimalField('Glycémie (g/L)', max_digits=4, decimal_places=2, null=True, blank=True)
    protein_in_urine = models.BooleanField('Protéine dans les urines', default=False)
    
    # HIV/STI screening
    hiv_test_done = models.BooleanField('Test VIH effectué', default=False)
    hiv_test_result = models.CharField('Résultat VIH', max_length=20, blank=True)
    syphilis_test_done = models.BooleanField('Test syphilis effectué', default=False)
    syphilis_test_result = models.CharField('Résultat syphilis', max_length=20, blank=True)
    
    # Preventive care
    iron_supplement_given = models.BooleanField('Fer prescrit', default=False)
    folic_acid_given = models.BooleanField('Acide folique prescrit', default=False)
    antimalarial_given = models.BooleanField('Antipaludique donné', default=False)
    tetanus_vaccine_given = models.BooleanField('Vaccin antitétanique', default=False)
    
    # Next appointment
    next_appointment_date = models.DateField('Prochain RDV', null=True, blank=True)
    next_cpn_type = models.CharField('Prochain type CPN', max_length=20, choices=CPN_TYPE_CHOICES, blank=True)
    
    # Staff
    conducted_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_cpn_consultations'
    )
    
    # Observations
    complaints = models.TextField('Plaintes', blank=True)
    examination_findings = models.TextField('Résultats de l\'examen', blank=True)
    diagnosis = models.TextField('Diagnostic', blank=True)
    treatment_plan = models.TextField('Plan de traitement', blank=True)
    referral_needed = models.BooleanField('Référence nécessaire', default=False)
    referral_reason = models.TextField('Raison de la référence', blank=True)
    
    notes = models.TextField('Notes', blank=True)
    
    class Meta:
        verbose_name = 'Consultation CPN'
        verbose_name_plural = 'Consultations CPN'
        ordering = ['-consultation_date']
        indexes = [
            models.Index(fields=['pregnancy', 'cpn_type']),
            models.Index(fields=['consultation_date']),
            models.Index(fields=['next_appointment_date']),
        ]
    
    def __str__(self):
        return f"{self.pregnancy.patient.get_full_name()} - {self.get_cpn_type_display()} - {self.consultation_date}"
    
    @property
    def is_high_blood_pressure(self):
        """Check if blood pressure is high"""
        return self.blood_pressure_systolic >= 140 or self.blood_pressure_diastolic >= 90
    
    @property
    def is_anemic(self):
        """Check if patient is anemic"""
        if self.hemoglobin:
            return self.hemoglobin < 11.0
        return False
    
    @property
    def bmi(self):
        """Calculate BMI at this consultation"""
        if self.weight and self.pregnancy.patient.height:
            height_m = float(self.pregnancy.patient.height) / 100
            return round(float(self.weight) / (height_m ** 2), 2)
        return None


class CPNReminder(TimeStampedModel):
    """CPN appointment reminders"""
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('SENT', 'Envoyé'),
        ('FAILED', 'Échec'),
    ]
    
    pregnancy = models.ForeignKey(Pregnancy, on_delete=models.CASCADE, related_name='reminders')
    cpn_consultation = models.ForeignKey(CPNConsultation, on_delete=models.SET_NULL, null=True, blank=True)
    reminder_date = models.DateField('Date du rappel')
    message = models.TextField('Message')
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField('Envoyé à', null=True, blank=True)
    error_message = models.TextField('Message d\'erreur', blank=True)
    
    class Meta:
        verbose_name = 'Rappel CPN'
        verbose_name_plural = 'Rappels CPN'
        ordering = ['-reminder_date']
    
    def __str__(self):
        return f"Rappel pour {self.pregnancy.patient.get_full_name()} - {self.reminder_date}"
