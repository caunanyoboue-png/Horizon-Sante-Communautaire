from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Purge RGPD: supprime les données non essentielles (notifications, logs SMS, audit logs) selon une rétention en jours."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="N'effectue aucune suppression, affiche seulement les compteurs")

        parser.add_argument("--notifications-days", type=int, default=90, help="Rétention notifications (jours)")
        parser.add_argument("--sms-days", type=int, default=180, help="Rétention logs SMS (jours)")
        parser.add_argument("--audit-days", type=int, default=365, help="Rétention audit logs (jours)")

        parser.add_argument(
            "--include-audit",
            action="store_true",
            help="Inclure AuditLog dans la purge (par défaut: non)",
        )

    def handle(self, *args, **options):
        dry_run = bool(options["dry_run"])

        notifications_days = int(options["notifications_days"])
        sms_days = int(options["sms_days"])
        audit_days = int(options["audit_days"])

        now = timezone.now()

        # Imports ici pour éviter tout problème de dépendance/cycle au chargement.
        from audit.models import AuditLog
        from messaging.models import Notification
        from patients.models import SmsLog

        def purge_queryset(qs, label: str) -> int:
            count = qs.count()
            if count == 0:
                self.stdout.write(f"{label}: 0")
                return 0
            if dry_run:
                self.stdout.write(f"{label}: {count} (dry-run)")
                return count
            deleted, _ = qs.delete()
            self.stdout.write(f"{label}: {count} supprimés")
            return deleted

        if notifications_days > 0:
            cutoff = now - timedelta(days=notifications_days)
            purge_queryset(Notification.objects.filter(created_at__lt=cutoff), f"Notifications > {notifications_days}j")
        else:
            self.stdout.write("Notifications: ignorées (notifications-days=0)")

        if sms_days > 0:
            cutoff = now - timedelta(days=sms_days)
            purge_queryset(SmsLog.objects.filter(created_at__lt=cutoff), f"SmsLog > {sms_days}j")
        else:
            self.stdout.write("SmsLog: ignorés (sms-days=0)")

        if options["include_audit"]:
            if audit_days > 0:
                cutoff = now - timedelta(days=audit_days)
                purge_queryset(AuditLog.objects.filter(created_at__lt=cutoff), f"AuditLog > {audit_days}j")
            else:
                self.stdout.write("AuditLog: ignorés (audit-days=0)")
        else:
            self.stdout.write("AuditLog: non inclus (utilise --include-audit pour activer)")
