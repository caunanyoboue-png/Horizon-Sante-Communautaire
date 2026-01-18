from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Exists, OuterRef
from django.utils import timezone

from patients.models import RendezVous, SmsLog
from patients.sms_provider import SmsProvider


class Command(BaseCommand):
    help = "Envoie des SMS de rappel pour les rendez-vous à venir et enregistre les logs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Fenêtre de rappel (en heures) pour les rendez-vous à venir (défaut: 24).",
        )

    def handle(self, *args, **options):
        hours = int(options["hours"])
        now = timezone.now()
        end = now + timedelta(hours=hours)

        provider = SmsProvider()

        already_sent = SmsLog.objects.filter(rendez_vous=OuterRef("pk"), statut=SmsLog.STATUT_SUCCES)

        rdvs = (
            RendezVous.objects.select_related("patient")
            .annotate(sent_ok=Exists(already_sent))
            .filter(statut="PLANIFIE", date_heure__gte=now, date_heure__lte=end, sent_ok=False)
            .order_by("date_heure")
        )

        total = 0
        success = 0
        failed = 0

        for rdv in rdvs:
            total += 1
            phone = (rdv.patient.telephone or "").strip()
            message = (
                f"Rappel ADJAHI: RDV le {rdv.date_heure:%d/%m/%Y à %H:%M}. "
                f"Patient: {rdv.patient.nom} {rdv.patient.prenoms}."
            )

            result = provider.send_sms(phone=phone, message=message)

            if result.success:
                success += 1
                SmsLog.objects.create(
                    rendez_vous=rdv,
                    telephone=phone,
                    message=message,
                    statut=SmsLog.STATUT_SUCCES,
                    provider=result.provider,
                    provider_message_id=result.message_id,
                )
            else:
                failed += 1
                SmsLog.objects.create(
                    rendez_vous=rdv,
                    telephone=phone,
                    message=message,
                    statut=SmsLog.STATUT_ECHEC,
                    provider=result.provider,
                    provider_message_id=result.message_id,
                    error_message=result.error,
                )

        self.stdout.write(self.style.SUCCESS(f"RDV ciblés: {total} | SMS succès: {success} | échecs: {failed}"))
