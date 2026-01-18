"""
Views for CPN (Consultation Prénatale) API
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.utils import timezone
from datetime import timedelta
from .models import Pregnancy, CPNConsultation, CPNReminder
from .serializers import (
    PregnancySerializer,
    PregnancyDetailSerializer,
    PregnancyCreateSerializer,
    CPNConsultationSerializer,
    CPNReminderSerializer
)
from apps.authentication.permissions import CanCreateCPN


@extend_schema_view(
    list=extend_schema(description="Liste de toutes les grossesses"),
    retrieve=extend_schema(description="Détails d'une grossesse"),
    create=extend_schema(description="Enregistrer une nouvelle grossesse"),
    update=extend_schema(description="Modifier une grossesse"),
)
class PregnancyViewSet(viewsets.ModelViewSet):
    """ViewSet for Pregnancy management"""
    
    queryset = Pregnancy.objects.all().select_related(
        'patient', 'assigned_midwife'
    ).prefetch_related('cpn_consultations')
    permission_classes = [permissions.IsAuthenticated, CanCreateCPN]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'risk_level', 'patient', 'assigned_midwife']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__patient_id']
    ordering_fields = ['expected_delivery_date', 'created_at', 'last_menstrual_period']
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'create':
            return PregnancyCreateSerializer
        elif self.action == 'retrieve':
            return PregnancyDetailSerializer
        return PregnancySerializer
    
    @extend_schema(
        description="Grossesses en cours",
        responses={200: PregnancySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        """Get all ongoing pregnancies"""
        pregnancies = self.queryset.filter(status='ONGOING').order_by('expected_delivery_date')
        serializer = self.get_serializer(pregnancies, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Grossesses à haut risque",
        responses={200: PregnancySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high-risk pregnancies"""
        pregnancies = self.queryset.filter(status='ONGOING', risk_level='HIGH')
        serializer = self.get_serializer(pregnancies, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Accouchements prévus ce mois",
        responses={200: PregnancySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def due_this_month(self, request):
        """Get pregnancies due this month"""
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        pregnancies = self.queryset.filter(
            status='ONGOING',
            expected_delivery_date__gte=start_of_month,
            expected_delivery_date__lte=end_of_month
        ).order_by('expected_delivery_date')
        
        serializer = self.get_serializer(pregnancies, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Statistiques des grossesses",
        responses={200: {
            'type': 'object',
            'properties': {
                'total': {'type': 'integer'},
                'ongoing': {'type': 'integer'},
                'high_risk': {'type': 'integer'},
                'due_this_month': {'type': 'integer'}
            }
        }}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get pregnancy statistics"""
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        stats = {
            'total': self.queryset.count(),
            'ongoing': self.queryset.filter(status='ONGOING').count(),
            'high_risk': self.queryset.filter(status='ONGOING', risk_level='HIGH').count(),
            'medium_risk': self.queryset.filter(status='ONGOING', risk_level='MEDIUM').count(),
            'low_risk': self.queryset.filter(status='ONGOING', risk_level='LOW').count(),
            'due_this_month': self.queryset.filter(
                status='ONGOING',
                expected_delivery_date__gte=start_of_month,
                expected_delivery_date__lte=end_of_month
            ).count(),
            'completed_this_year': self.queryset.filter(
                status='COMPLETED',
                actual_delivery_date__year=today.year
            ).count(),
        }
        
        return Response(stats)


@extend_schema_view(
    list=extend_schema(description="Liste de toutes les consultations CPN"),
    retrieve=extend_schema(description="Détails d'une consultation CPN"),
    create=extend_schema(description="Créer une consultation CPN"),
    update=extend_schema(description="Modifier une consultation CPN"),
)
class CPNConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet for CPN Consultations"""
    
    queryset = CPNConsultation.objects.all().select_related(
        'pregnancy__patient', 'conducted_by'
    )
    serializer_class = CPNConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateCPN]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pregnancy', 'cpn_type', 'conducted_by']
    search_fields = ['pregnancy__patient__first_name', 'pregnancy__patient__last_name']
    ordering_fields = ['consultation_date', 'created_at']
    
    def perform_create(self, serializer):
        """Set conducted_by to current user"""
        serializer.save(conducted_by=self.request.user)
    
    @extend_schema(
        description="CPN1 consultations (première consultation avant 16 SA)",
        responses={200: CPNConsultationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def cpn1(self, request):
        """Get all CPN1 consultations"""
        consultations = self.queryset.filter(cpn_type='CPN1')
        serializer = self.get_serializer(consultations, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Consultations avec tension élevée",
        responses={200: CPNConsultationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def high_blood_pressure(self, request):
        """Get consultations with high blood pressure"""
        from django.db.models import Q
        consultations = self.queryset.filter(
            Q(blood_pressure_systolic__gte=140) | Q(blood_pressure_diastolic__gte=90)
        )
        serializer = self.get_serializer(consultations, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Consultations avec anémie",
        responses={200: CPNConsultationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def anemic(self, request):
        """Get consultations with anemia"""
        consultations = self.queryset.filter(hemoglobin__lt=11.0)
        serializer = self.get_serializer(consultations, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Statistiques des consultations CPN",
        responses={200: {
            'type': 'object',
            'properties': {
                'total': {'type': 'integer'},
                'by_type': {'type': 'object'}
            }
        }}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get CPN consultation statistics"""
        from django.db.models import Count, Q
        
        stats = {
            'total': self.queryset.count(),
            'by_type': dict(self.queryset.values('cpn_type').annotate(
                count=Count('cpn_type')
            ).values_list('cpn_type', 'count')),
            'high_blood_pressure': self.queryset.filter(
                Q(blood_pressure_systolic__gte=140) | Q(blood_pressure_diastolic__gte=90)
            ).count(),
            'anemic': self.queryset.filter(hemoglobin__lt=11.0).count(),
            'hiv_positive': self.queryset.filter(hiv_test_result__icontains='positif').count(),
            'referrals_needed': self.queryset.filter(referral_needed=True).count(),
        }
        
        return Response(stats)


@extend_schema_view(
    list=extend_schema(description="Liste des rappels CPN"),
    retrieve=extend_schema(description="Détails d'un rappel CPN"),
    create=extend_schema(description="Créer un rappel CPN"),
)
class CPNReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for CPN Reminders"""
    
    queryset = CPNReminder.objects.all().select_related('pregnancy__patient')
    serializer_class = CPNReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pregnancy', 'status']
    ordering_fields = ['reminder_date', 'created_at']
    
    @extend_schema(
        description="Rappels en attente d'envoi",
        responses={200: CPNReminderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending reminders"""
        today = timezone.now().date()
        reminders = self.queryset.filter(
            status='PENDING',
            reminder_date__lte=today
        )
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Envoyer un rappel manuel",
        responses={200: {'description': 'Rappel envoyé avec succès'}}
    )
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a reminder manually"""
        reminder = self.get_object()
        
        # Import task for sending SMS
        from apps.notifications.tasks import send_cpn_reminder_sms
        
        try:
            # Send SMS asynchronously
            send_cpn_reminder_sms.delay(reminder.id)
            
            return Response({
                'success': True,
                'message': 'Rappel en cours d\'envoi.'
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
