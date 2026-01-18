from django.urls import path

from .views import export_consultations, export_patients, rapport_mensuel_pdf, reports_home

urlpatterns = [
    path("reports/", reports_home, name="reports-home"),
    path("reports/patients.xlsx", export_patients, name="reports-patients-xlsx"),
    path("reports/consultations.xlsx", export_consultations, name="reports-consultations-xlsx"),
    path("reports/rapport-mensuel.pdf", rapport_mensuel_pdf, name="reports-mensuel-pdf"),
]
