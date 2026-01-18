"""
Serializers for CPN (Consultation Prénatale) API
"""

from rest_framework import serializers
from .models import Pregnancy, CPNConsultation, CPNReminder
from apps.patients.serializers import PatientListSerializer


class PregnancySerializer(serializers.ModelSerializer):
    """Serializer for Pregnancy"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    assigned_midwife_name = serializers.CharField(source='assigned_midwife.get_full_name', read_only=True)
    gestational_age_weeks = serializers.IntegerField(read_only=True)
    gestational_age_display = serializers.CharField(read_only=True)
    trimester = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Pregnancy
        fields = [
            'id', 'patient', 'patient_name', 'pregnancy_number', 'parity',
            'last_menstrual_period', 'expected_delivery_date', 'actual_delivery_date',
            'status', 'risk_level', 'blood_group_verified', 'rh_factor',
            'has_diabetes', 'has_hypertension', 'has_anemia', 'other_risks',
            'assigned_midwife', 'assigned_midwife_name', 'notes',
            'gestational_age_weeks', 'gestational_age_display', 'trimester',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'expected_delivery_date', 'created_at', 'updated_at']


class PregnancyDetailSerializer(PregnancySerializer):
    """Detailed pregnancy serializer with CPN consultations"""
    
    cpn_consultations = serializers.SerializerMethodField()
    patient = PatientListSerializer(read_only=True)
    
    class Meta(PregnancySerializer.Meta):
        fields = PregnancySerializer.Meta.fields + ['cpn_consultations']
    
    def get_cpn_consultations(self, obj):
        consultations = obj.cpn_consultations.all().order_by('-consultation_date')
        return CPNConsultationSerializer(consultations, many=True).data


class CPNConsultationSerializer(serializers.ModelSerializer):
    """Serializer for CPN Consultation"""
    
    patient_name = serializers.CharField(source='pregnancy.patient.get_full_name', read_only=True)
    conducted_by_name = serializers.CharField(source='conducted_by.get_full_name', read_only=True)
    is_high_blood_pressure = serializers.BooleanField(read_only=True)
    is_anemic = serializers.BooleanField(read_only=True)
    bmi = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = CPNConsultation
        fields = [
            'id', 'pregnancy', 'patient_name', 'cpn_type', 'consultation_date',
            'gestational_age_weeks', 'weight', 'blood_pressure_systolic',
            'blood_pressure_diastolic', 'temperature', 'fundal_height',
            'fetal_heart_rate', 'hemoglobin', 'glucose', 'protein_in_urine',
            'hiv_test_done', 'hiv_test_result', 'syphilis_test_done',
            'syphilis_test_result', 'iron_supplement_given', 'folic_acid_given',
            'antimalarial_given', 'tetanus_vaccine_given',
            'next_appointment_date', 'next_cpn_type', 'conducted_by',
            'conducted_by_name', 'complaints', 'examination_findings',
            'diagnosis', 'treatment_plan', 'referral_needed', 'referral_reason',
            'notes', 'is_high_blood_pressure', 'is_anemic', 'bmi',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CPNReminderSerializer(serializers.ModelSerializer):
    """Serializer for CPN Reminder"""
    
    patient_name = serializers.CharField(source='pregnancy.patient.get_full_name', read_only=True)
    patient_phone = serializers.CharField(source='pregnancy.patient.phone', read_only=True)
    
    class Meta:
        model = CPNReminder
        fields = [
            'id', 'pregnancy', 'patient_name', 'patient_phone',
            'cpn_consultation', 'reminder_date', 'message', 'status',
            'sent_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'created_at']


class PregnancyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new pregnancy"""
    
    class Meta:
        model = Pregnancy
        fields = [
            'patient', 'pregnancy_number', 'parity', 'last_menstrual_period',
            'blood_group_verified', 'rh_factor', 'has_diabetes',
            'has_hypertension', 'has_anemia', 'other_risks',
            'assigned_midwife', 'notes'
        ]
    
    def validate_patient(self, value):
        """Validate that patient is female"""
        if value.gender != 'F':
            raise serializers.ValidationError("Le patient doit être de sexe féminin.")
        return value
    
    def validate(self, attrs):
        """Additional validation"""
        # Check for active pregnancy
        if attrs['patient'].pregnancies.filter(status='ONGOING').exists():
            raise serializers.ValidationError({
                'patient': 'Cette patiente a déjà une grossesse en cours.'
            })
        return attrs
