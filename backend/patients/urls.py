from django.urls import path

from .views import (
    consultation_create,
    cpn_create,
    ordonnance_create,
    ordonnance_detail,
    ordonnance_pdf,
    patient_anonymize,
    patient_create,
    patient_detail,
    patient_export_json,
    patient_list,
    patient_update,
    rdv_create,
)

urlpatterns = [
    path("patients/", patient_list, name="patient-list"),
    path("patients/nouveau/", patient_create, name="patient-create"),
    path("patients/<int:pk>/", patient_detail, name="patient-detail"),
    path("patients/<int:pk>/modifier/", patient_update, name="patient-update"),
    path("patients/<int:pk>/export.json", patient_export_json, name="patient-export-json"),
    path("patients/<int:pk>/anonymiser/", patient_anonymize, name="patient-anonymize"),
    path("patients/<int:pk>/cpn/nouveau/", cpn_create, name="cpn-create"),
    path("patients/<int:pk>/rdv/nouveau/", rdv_create, name="rdv-create"),
    path("patients/<int:pk>/consultations/nouveau/", consultation_create, name="consultation-create"),
    path("patients/<int:pk>/ordonnances/nouveau/", ordonnance_create, name="ordonnance-create"),
    path(
        "patients/<int:pk>/ordonnances/<int:ordonnance_id>/",
        ordonnance_detail,
        name="ordonnance-detail",
    ),
    path(
        "patients/<int:pk>/ordonnances/<int:ordonnance_id>/pdf/",
        ordonnance_pdf,
        name="ordonnance-pdf",
    ),
]
