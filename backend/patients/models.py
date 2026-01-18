from django.db import models


class Patient(models.Model):
    # Identité
    code_patient = models.CharField(max_length=32, unique=True)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(
        max_length=1,
        choices=[("F", "Femme"), ("M", "Homme")],
        null=True,
        blank=True,
    )

    # Contact / localisation
    telephone = models.CharField(max_length=30, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    zone = models.CharField(
        max_length=50,
        choices=[("GRAND_BASSAM", "Grand-Bassam"), ("BONOUA", "Bonoua")],
        default="GRAND_BASSAM",
    )

    # Informations médicales (phase 1 : simplifié)
    antecedents = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nom", "prenoms"]

    def __str__(self) -> str:
        return f"{self.code_patient} - {self.nom} {self.prenoms}"


class Consultation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="consultations")
    date_consultation = models.DateTimeField()
    motif = models.CharField(max_length=255, blank=True)
    observation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_consultation"]

    def __str__(self) -> str:
        return f"Consultation {self.patient.code_patient} - {self.date_consultation:%Y-%m-%d}"


class SuiviCPN(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="suivis_cpn")
    numero = models.PositiveSmallIntegerField(
        choices=[(1, "CPN1"), (2, "CPN2"), (3, "CPN3"), (4, "CPN4")]
    )
    date = models.DateField()
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("patient", "numero")
        ordering = ["patient", "numero"]

    def __str__(self) -> str:
        return f"{self.patient.code_patient} - CPN{self.numero}"


class RendezVous(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="rendez_vous")
    date_heure = models.DateTimeField()
    objet = models.CharField(max_length=255, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=[("PLANIFIE", "Planifié"), ("EFFECTUE", "Effectué"), ("ANNULE", "Annulé")],
        default="PLANIFIE",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_heure"]

    def __str__(self) -> str:
        return f"RDV {self.patient.code_patient} - {self.date_heure:%Y-%m-%d %H:%M}"


class Ordonnance(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="ordonnances")
    date = models.DateField()
    diagnostic = models.CharField(max_length=255, blank=True)
    instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        return f"Ordonnance {self.patient.code_patient} - {self.date:%Y-%m-%d}"


class LigneOrdonnance(models.Model):
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE, related_name="lignes")
    medicament = models.CharField(max_length=255)
    posologie = models.CharField(max_length=255, blank=True)
    duree = models.CharField(max_length=100, blank=True)
    commentaire = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.medicament


class CasSuivi(models.Model):
    TYPE_VIH = "VIH"
    TYPE_TB = "TB"

    STATUT_SUSPECT = "SUSPECT"
    STATUT_CONFIRME = "CONFIRME"
    STATUT_SUIVI = "SUIVI"
    STATUT_CLOTURE = "CLOTURE"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="cas_suivi")
    type_cas = models.CharField(
        max_length=10,
        choices=[(TYPE_VIH, "VIH/Sida"), (TYPE_TB, "Tuberculose")],
    )
    statut = models.CharField(
        max_length=10,
        choices=[
            (STATUT_SUSPECT, "Suspect"),
            (STATUT_CONFIRME, "Confirmé"),
            (STATUT_SUIVI, "En suivi"),
            (STATUT_CLOTURE, "Clôturé"),
        ],
        default=STATUT_SUIVI,
    )
    date_signalement = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.patient.code_patient} - {self.type_cas} ({self.statut})"


class SmsLog(models.Model):
    STATUT_SUCCES = "SUCCES"
    STATUT_ECHEC = "ECHEC"

    rendez_vous = models.ForeignKey(RendezVous, on_delete=models.CASCADE, related_name="sms_logs")
    telephone = models.CharField(max_length=30)
    message = models.TextField()
    statut = models.CharField(
        max_length=10,
        choices=[(STATUT_SUCCES, "Succès"), (STATUT_ECHEC, "Échec")],
    )
    provider = models.CharField(max_length=50, blank=True)
    provider_message_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"SMS {self.statut} - {self.telephone}"
