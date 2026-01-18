from django.db import models

from patients.models import Patient


class Pathologie(models.Model):
    code = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=100)

    class Meta:
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom


class DossierCommunautaire(models.Model):
    STATUT_SUIVI = "SUIVI"
    STATUT_STABLE = "STABLE"
    STATUT_TERMINE = "TERMINE"
    STATUT_DECEDE = "DECEDE"

    STATUT_CHOICES = [
        (STATUT_SUIVI, "En suivi"),
        (STATUT_STABLE, "Stable"),
        (STATUT_TERMINE, "Terminé"),
        (STATUT_DECEDE, "Décédé"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="dossiers_communautaires")
    pathologie = models.ForeignKey(Pathologie, on_delete=models.PROTECT, related_name="dossiers")

    date_diagnostic = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SUIVI)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_diagnostic", "-id"]

    def __str__(self) -> str:
        return f"{self.patient.code_patient} - {self.pathologie.code}"


class SuiviCommunautaire(models.Model):
    dossier = models.ForeignKey(DossierCommunautaire, on_delete=models.CASCADE, related_name="suivis")
    date = models.DateField()
    observation = models.TextField(blank=True)
    traitement = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        return f"Suivi {self.dossier_id} - {self.date:%Y-%m-%d}"
