"""
URL Configuration for CPN API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PregnancyViewSet, CPNConsultationViewSet, CPNReminderViewSet

router = DefaultRouter()
router.register('pregnancies', PregnancyViewSet, basename='pregnancy')
router.register('consultations', CPNConsultationViewSet, basename='cpn-consultation')
router.register('reminders', CPNReminderViewSet, basename='cpn-reminder')

urlpatterns = [
    path('', include(router.urls)),
]
