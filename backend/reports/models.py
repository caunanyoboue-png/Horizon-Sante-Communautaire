from django.conf import settings
from django.db import models


class Rapport(models.Model):
    TYPE_PATIENTS_XLSX = "PATIENTS_XLSX"
    TYPE_CONSULTATIONS_XLSX = "CONSULTATIONS_XLSX"
    TYPE_MENSUEL_PDF = "MENSUEL_PDF"

    TYPE_CHOICES = [
        (TYPE_PATIENTS_XLSX, "Export Patients (Excel)"),
        (TYPE_CONSULTATIONS_XLSX, "Export Consultations (Excel)"),
        (TYPE_MENSUEL_PDF, "Rapport Mensuel (PDF)"),
    ]

    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    params = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.type} - {self.created_at:%Y-%m-%d %H:%M}"
