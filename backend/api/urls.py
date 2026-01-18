from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DashboardSummaryView, HealthView
from .viewsets import (
    ConsultationViewSet,
    DossierCommunautaireViewSet,
    LigneOrdonnanceViewSet,
    MessageViewSet,
    NotificationViewSet,
    OrdonnanceViewSet,
    PathologieViewSet,
    PatientViewSet,
    RendezVousViewSet,
    SuiviCommunautaireViewSet,
    SuiviCPNViewSet,
    ThreadViewSet,
)

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"consultations", ConsultationViewSet, basename="consultation")
router.register(r"cpn", SuiviCPNViewSet, basename="cpn")
router.register(r"rendez-vous", RendezVousViewSet, basename="rendezvous")
router.register(r"ordonnances", OrdonnanceViewSet, basename="ordonnance")
router.register(r"ordonnance-lignes", LigneOrdonnanceViewSet, basename="ordonnance-ligne")
router.register(r"pathologies", PathologieViewSet, basename="pathologie")
router.register(r"dossiers-communautaires", DossierCommunautaireViewSet, basename="dossier-communautaire")
router.register(r"suivis-communautaires", SuiviCommunautaireViewSet, basename="suivi-communautaire")
router.register(r"threads", ThreadViewSet, basename="thread")
router.register(r"messages", MessageViewSet, basename="message")
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("health/", HealthView.as_view(), name="api-health"),
    path("dashboard/summary/", DashboardSummaryView.as_view(), name="api-dashboard-summary"),
    path("", include(router.urls)),
]
