from __future__ import annotations

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

from patients.models import Patient

User = get_user_model()

class Command(BaseCommand):
    help = "Anonymise les patients inactifs depuis une certaine période (RGPD - Droit à l'oubli)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--years",
            type=int,
            default=5,
            help="Nombre d'années d'inactivité avant anonymisation (défaut: 5 ans)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche les patients à anonymiser sans effectuer l'action",
        )

    def handle(self, *args, **options):
        years = options["years"]
        dry_run = options["dry_run"]
        cutoff_date = timezone.now() - timedelta(days=years * 365)

        # Critère d'inactivité : date_dernier_acces < cutoff OU (date_dernier_acces IS NULL ET updated_at < cutoff)
        patients = Patient.objects.filter(
            Q(date_dernier_acces__lt=cutoff_date) | 
            Q(date_dernier_acces__isnull=True, updated_at__lt=cutoff_date)
        ).exclude(nom__startswith="ANONYME") # Éviter de ré-anonymiser

        count = patients.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(f"Aucun patient inactif depuis {years} ans trouvé."))
            return

        self.stdout.write(f"Patients inactifs trouvés (> {years} ans): {count}")

        if dry_run:
            for p in patients:
                self.stdout.write(f" - [Dry-Run] {p.nom} {p.prenoms} (Dernier accès: {p.date_dernier_acces or p.updated_at})")
            return

        anonymized_count = 0
        for p in patients:
            try:
                original_name = f"{p.nom} {p.prenoms}"
                
                # Anonymisation Patient
                p.nom = f"ANONYME_{p.id}"
                p.prenoms = "Inconnu"
                p.telephone = ""
                p.adresse = ""
                p.antecedents = "DONNÉES ANONYMISÉES"
                p.save()

                # Désactivation User lié
                if p.user:
                    u = p.user
                    u.is_active = False
                    u.username = f"anonyme_{p.id}_{u.id}" # Pour éviter contrainte unique
                    u.email = ""
                    u.first_name = "ANONYME"
                    u.last_name = ""
                    u.save()

                anonymized_count += 1
                self.stdout.write(f"Anonymisé: {original_name} -> {p.nom}")
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Erreur anonymisation patient {p.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Terminé. {anonymized_count} patients anonymisés."))
