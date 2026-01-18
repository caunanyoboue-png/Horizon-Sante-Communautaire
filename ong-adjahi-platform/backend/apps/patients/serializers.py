"""
Serializers for Patients API
"""

from rest_framework import serializers
from .models import Patient, MedicalHistory, Allergy, Medication


class MedicalHistorySerializer(serializers.ModelSerializer):
    """Serializer for medical history"""
    
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = MedicalHistory
        fields = [
            'id', 'patient', 'condition', 'diagnosis_date', 'treatment',
            'is_chronic', 'is_active', 'notes', 'recorded_by', 'recorded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AllergySerializer(serializers.ModelSerializer):
    """Serializer for allergies"""
    
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    
    class Meta:
        model = Allergy
        fields = [
            'id', 'patient', 'allergen', 'reaction', 'severity',
            'diagnosed_date', 'is_active', 'recorded_by', 'recorded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for medications"""
    
    prescribed_by_name = serializers.CharField(source='prescribed_by.get_full_name', read_only=True)
    
    class Meta:
        model = Medication
        fields = [
            'id', 'patient', 'name', 'dosage', 'frequency',
            'start_date', 'end_date', 'reason', 'is_active',
            'prescribed_by', 'prescribed_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient CRUD operations"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    bmi = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    registered_by_name = serializers.CharField(source='registered_by.get_full_name', read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'age', 'gender', 'phone', 'email', 'address', 'city',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'blood_group', 'height', 'weight', 'bmi',
            'marital_status', 'occupation',
            'registration_location', 'registered_by', 'registered_by_name',
            'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient_id', 'age', 'bmi', 'created_at', 'updated_at']


class PatientDetailSerializer(PatientSerializer):
    """Detailed patient serializer with related data"""
    
    medical_histories = MedicalHistorySerializer(many=True, read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)
    medications = MedicationSerializer(many=True, read_only=True)
    
    class Meta(PatientSerializer.Meta):
        fields = PatientSerializer.Meta.fields + [
            'medical_histories', 'allergies', 'medications'
        ]


class PatientListSerializer(serializers.ModelSerializer):
    """Minimal patient serializer for lists"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'full_name', 'age', 'gender',
            'phone', 'city', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'patient_id', 'age', 'created_at']
