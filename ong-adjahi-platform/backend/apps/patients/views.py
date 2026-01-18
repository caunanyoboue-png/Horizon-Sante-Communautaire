"""
Views for Patients API
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Patient, MedicalHistory, Allergy, Medication
from .serializers import (
    PatientSerializer,
    PatientDetailSerializer,
    PatientListSerializer,
    MedicalHistorySerializer,
    AllergySerializer,
    MedicationSerializer
)
from apps.authentication.permissions import CanManagePatients


@extend_schema_view(
    list=extend_schema(description="Liste de tous les patients"),
    retrieve=extend_schema(description="Détails d'un patient"),
    create=extend_schema(description="Enregistrer un nouveau patient"),
    update=extend_schema(description="Modifier un patient"),
    destroy=extend_schema(description="Supprimer un patient"),
)
class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for Patient CRUD operations"""
    
    queryset = Patient.objects.all().select_related('registered_by').prefetch_related(
        'medical_histories', 'allergies', 'medications'
    )
    permission_classes = [permissions.IsAuthenticated, CanManagePatients]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['gender', 'city', 'is_active', 'blood_group']
    search_fields = ['patient_id', 'first_name', 'last_name', 'phone', 'email']
    ordering_fields = ['created_at', 'last_name', 'date_of_birth']
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'list':
            return PatientListSerializer
        elif self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientSerializer
    
    def perform_create(self, serializer):
        """Set registered_by to current user"""
        serializer.save(registered_by=self.request.user)
    
    @extend_schema(
        description="Obtenir les antécédents médicaux d'un patient",
        responses={200: MedicalHistorySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def medical_history(self, request, pk=None):
        """Get patient medical history"""
        patient = self.get_object()
        histories = patient.medical_histories.filter(is_active=True)
        serializer = MedicalHistorySerializer(histories, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Ajouter un antécédent médical",
        request=MedicalHistorySerializer,
        responses={201: MedicalHistorySerializer}
    )
    @action(detail=True, methods=['post'])
    def add_medical_history(self, request, pk=None):
        """Add medical history entry"""
        patient = self.get_object()
        serializer = MedicalHistorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(patient=patient, recorded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        description="Obtenir les allergies d'un patient",
        responses={200: AllergySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def allergies(self, request, pk=None):
        """Get patient allergies"""
        patient = self.get_object()
        allergies = patient.allergies.filter(is_active=True).order_by('-severity')
        serializer = AllergySerializer(allergies, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Ajouter une allergie",
        request=AllergySerializer,
        responses={201: AllergySerializer}
    )
    @action(detail=True, methods=['post'])
    def add_allergy(self, request, pk=None):
        """Add allergy"""
        patient = self.get_object()
        serializer = AllergySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(patient=patient, recorded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        description="Obtenir les médicaments actuels d'un patient",
        responses={200: MedicationSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def medications(self, request, pk=None):
        """Get patient current medications"""
        patient = self.get_object()
        medications = patient.medications.filter(is_active=True)
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Prescrire un médicament",
        request=MedicationSerializer,
        responses={201: MedicationSerializer}
    )
    @action(detail=True, methods=['post'])
    def prescribe_medication(self, request, pk=None):
        """Prescribe medication"""
        patient = self.get_object()
        serializer = MedicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(patient=patient, prescribed_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        description="Statistiques des patients",
        responses={200: {
            'type': 'object',
            'properties': {
                'total': {'type': 'integer'},
                'by_gender': {'type': 'object'},
                'by_city': {'type': 'object'},
                'by_age_group': {'type': 'object'}
            }
        }}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get patient statistics"""
        from django.db.models import Count, Q
        from django.utils import timezone
        
        today = timezone.now().date()
        
        stats = {
            'total': Patient.objects.filter(is_active=True).count(),
            'by_gender': dict(Patient.objects.filter(is_active=True).values('gender').annotate(count=Count('gender')).values_list('gender', 'count')),
            'by_city': dict(Patient.objects.filter(is_active=True).values('city').annotate(count=Count('city')).values_list('city', 'count')),
        }
        
        return Response(stats)


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Medical History"""
    
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [permissions.IsAuthenticated, CanManagePatients]
    filterset_fields = ['patient', 'is_chronic', 'is_active']
    search_fields = ['condition', 'treatment']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class AllergyViewSet(viewsets.ModelViewSet):
    """ViewSet for Allergies"""
    
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [permissions.IsAuthenticated, CanManagePatients]
    filterset_fields = ['patient', 'severity', 'is_active']
    search_fields = ['allergen', 'reaction']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)


class MedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Medications"""
    
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated, CanManagePatients]
    filterset_fields = ['patient', 'is_active']
    search_fields = ['name', 'reason']
    
    def perform_create(self, serializer):
        serializer.save(prescribed_by=self.request.user)
