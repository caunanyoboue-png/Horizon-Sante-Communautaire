from rest_framework import viewsets

from community.models import DossierCommunautaire, Pathologie, SuiviCommunautaire
from messaging.models import Message, Notification, Thread
from patients.models import Consultation, LigneOrdonnance, Ordonnance, Patient, RendezVous, SuiviCPN

from .serializers import (
    ConsultationSerializer,
    LigneOrdonnanceSerializer,
    DossierCommunautaireSerializer,
    MessageSerializer,
    NotificationSerializer,
    PathologieSerializer,
    OrdonnanceSerializer,
    PatientSerializer,
    RendezVousSerializer,
    SuiviCommunautaireSerializer,
    SuiviCPNSerializer,
    ThreadSerializer,
)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.select_related("patient").all()
    serializer_class = ConsultationSerializer


class SuiviCPNViewSet(viewsets.ModelViewSet):
    queryset = SuiviCPN.objects.select_related("patient").all()
    serializer_class = SuiviCPNSerializer


class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.select_related("patient").all()
    serializer_class = RendezVousSerializer


class OrdonnanceViewSet(viewsets.ModelViewSet):
    queryset = Ordonnance.objects.select_related("patient").prefetch_related("lignes").all()
    serializer_class = OrdonnanceSerializer


class LigneOrdonnanceViewSet(viewsets.ModelViewSet):
    queryset = LigneOrdonnance.objects.select_related("ordonnance", "ordonnance__patient").all()
    serializer_class = LigneOrdonnanceSerializer


class PathologieViewSet(viewsets.ModelViewSet):
    queryset = Pathologie.objects.all()
    serializer_class = PathologieSerializer


class DossierCommunautaireViewSet(viewsets.ModelViewSet):
    queryset = DossierCommunautaire.objects.select_related("patient", "pathologie").prefetch_related("suivis").all()
    serializer_class = DossierCommunautaireSerializer


class SuiviCommunautaireViewSet(viewsets.ModelViewSet):
    queryset = SuiviCommunautaire.objects.select_related("dossier", "dossier__patient", "dossier__pathologie").all()
    serializer_class = SuiviCommunautaireSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all().prefetch_related("participants")
    serializer_class = ThreadSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related("thread", "sender").all()
    serializer_class = MessageSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related("user").all()
    serializer_class = NotificationSerializer
