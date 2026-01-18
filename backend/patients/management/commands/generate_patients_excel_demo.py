from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Génère un fichier Excel (.xlsx) de démo pour l'import patients."

    def add_arguments(self, parser):
        parser.add_argument(
            "--out",
            default="patients_demo.xlsx",
            help="Chemin de sortie du fichier Excel (.xlsx)",
        )
        parser.add_argument(
            "--rows",
            type=int,
            default=8,
            help="Nombre de lignes patients à générer (min 1)",
        )

    def handle(self, *args, **options):
        try:
            from openpyxl import Workbook
        except ModuleNotFoundError as exc:
            raise CommandError("openpyxl manquant. Installe: pip install -r requirements.txt") from exc

        out_path = options["out"]
        rows = int(options["rows"])
        if rows < 1:
            raise CommandError("--rows doit être >= 1")

        wb = Workbook()
        ws = wb.active
        ws.title = "Patients"

        headers = [
            "code_patient",
            "nom",
            "prenoms",
            "telephone",
            "adresse",
            "zone",
            "sexe",
            "date_naissance",
            "antecedents",
        ]
        ws.append(headers)

        base = [
            {
                "code_patient": "P-0001",
                "nom": "KOUASSI",
                "prenoms": "Awa",
                "telephone": "+2250102030405",
                "adresse": "Quartier Sud",
                "zone": "Bonoua",
                "sexe": "F",
                "date_naissance": date(1998, 5, 12),
                "antecedents": "RAS",
            },
            {
                "code_patient": "P-0002",
                "nom": "KOFFI",
                "prenoms": "Yao",
                "telephone": "+2250708091011",
                "adresse": "Quartier Nord",
                "zone": "Grand Bassam",
                "sexe": "M",
                "date_naissance": date(1992, 11, 3),
                "antecedents": "HTA",
            },
            {
                "code_patient": "P-0003",
                "nom": "TRAORE",
                "prenoms": "Mariam",
                "telephone": "+2250506070809",
                "adresse": "Centre-ville",
                "zone": "Bonoua",
                "sexe": "Femme",
                "date_naissance": date(2001, 2, 20),
                "antecedents": "Diabète",
            },
            {
                "code_patient": "P-0004",
                "nom": "YAO",
                "prenoms": "Kader",
                "telephone": "+2250203040506",
                "adresse": "Route principale",
                "zone": "Bassam",
                "sexe": "Homme",
                "date_naissance": date(1988, 7, 8),
                "antecedents": "Asthme",
            },
        ]

        zones = ["Bonoua", "Grand Bassam", "Bassam"]
        sexes = ["F", "M", "Femme", "Homme"]

        for i in range(rows):
            if i < len(base):
                r = base[i]
            else:
                idx = i + 1
                r = {
                    "code_patient": f"P-{idx:04d}",
                    "nom": f"NOM{idx}",
                    "prenoms": f"Prenoms{idx}",
                    "telephone": f"+22501{idx:08d}"[-13:],
                    "adresse": f"Adresse {idx}",
                    "zone": zones[i % len(zones)],
                    "sexe": sexes[i % len(sexes)],
                    "date_naissance": date(1990 + (i % 15), ((i % 12) + 1), ((i % 28) + 1)),
                    "antecedents": "RAS",
                }

            ws.append([
                r["code_patient"],
                r["nom"],
                r["prenoms"],
                r["telephone"],
                r["adresse"],
                r["zone"],
                r["sexe"],
                r["date_naissance"],
                r["antecedents"],
            ])

        wb.save(out_path)
        self.stdout.write(self.style.SUCCESS(f"Fichier Excel de démo généré: {out_path}"))
