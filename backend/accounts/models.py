from django.conf import settings
from django.db import models


class Profil(models.Model):
    ROLE_ADMIN = "ADMIN"
    ROLE_MEDECIN = "MEDECIN"
    ROLE_SAGE_FEMME = "SAGE_FEMME"
    ROLE_AGENT = "AGENT_COMMUNAUTAIRE"
    ROLE_PSY = "PSYCHOLOGUE"
    ROLE_PATIENT = "PATIENT"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrateur"),
        (ROLE_MEDECIN, "Médecin"),
        (ROLE_SAGE_FEMME, "Sage-femme"),
        (ROLE_AGENT, "Agent communautaire"),
        (ROLE_PSY, "Psychologue"),
        (ROLE_PATIENT, "Patient"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_AGENT)
    telephone = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"
