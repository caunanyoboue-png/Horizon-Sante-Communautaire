from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from audit.models import AuditLog
from patients.models import Patient


class Command(BaseCommand):
    help = "Anonymise les patients inactifs depuis plus de 3 ans conformément au RGPD."

    def add_arguments(self, parser):
        parser.add_argument(
            "--years",
            type=int,
            default=3,
            help="Nombre d'années d'inactivité avant anonymisation (défaut: 3).",
        )

    def handle(self, *args, **options):
        years = int(options["years"])
        now = timezone.now()
        cutoff = now - timedelta(days=365 * years)

        qs = Patient.objects.filter(
            Q(date_dernier_acces__lt=cutoff)
            | (Q(date_dernier_acces__isnull=True) & Q(created_at__lt=cutoff))
        ).exclude(nom="ANONYMISE")

        total = qs.count()
        anonymised = 0

        for patient in qs.iterator():
            original_code = patient.code_patient

            patient.nom = "ANONYMISE"
            patient.prenoms = f"PATIENT_{patient.pk}"
            patient.telephone = ""
            patient.adresse = ""
            patient.antecedents = ""
            patient.date_naissance = None
            patient.date_dernier_acces = None
            patient.save(
                update_fields=[
                    "nom",
                    "prenoms",
                    "telephone",
                    "adresse",
                    "antecedents",
                    "date_naissance",
                    "date_dernier_acces",
                    "updated_at",
                ]
            )

            AuditLog.objects.create(
                user=None,
                action=AuditLog.ACTION_UPDATE,
                app_label="patients",
                model="patient",
                object_id=str(patient.pk),
                object_repr=str(patient),
                ip_address="",
                user_agent="rgpd_cleanup",
                extra={
                    "anonymized": True,
                    "previous_code_patient": original_code,
                    "source": "rgpd_cleanup",
                    "cutoff": cutoff.isoformat(),
                },
            )

            anonymised += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Patients ciblés: {total} | Patients anonymisés: {anonymised}"
            )
        )

