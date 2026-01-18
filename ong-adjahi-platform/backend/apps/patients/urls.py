"""
URL Configuration for Patients API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, MedicalHistoryViewSet, AllergyViewSet, MedicationViewSet

router = DefaultRouter()
router.register('', PatientViewSet, basename='patient')
router.register('medical-histories', MedicalHistoryViewSet, basename='medical-history')
router.register('allergies', AllergyViewSet, basename='allergy')
router.register('medications', MedicationViewSet, basename='medication')

urlpatterns = [
    path('', include(router.urls)),
]
