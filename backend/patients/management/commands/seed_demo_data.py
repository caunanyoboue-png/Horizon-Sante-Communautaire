from __future__ import annotations

import random
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Génère des données de démo (patients + CPN + RDV + consultations + ordonnances)."

    def add_arguments(self, parser):
        parser.add_argument("--patients", type=int, default=20)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--with-ordonnances", action="store_true")
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        from patients.models import (
            Consultation,
            LigneOrdonnance,
            Ordonnance,
            Patient,
            RendezVous,
            SuiviCPN,
        )

        n_patients = int(options["patients"])
        rng = random.Random(int(options["seed"]))
        with_ordonnances = bool(options["with_ordonnances"])
        reset = bool(options["reset"])

        today = timezone.localdate()

        noms = [
            "KOUASSI",
            "KOFFI",
            "YAO",
            "TRAORE",
            "DIABATE",
            "KONE",
            "OUATTARA",
            "TOURE",
            "BAMBA",
            "KAMARA",
        ]
        prenoms = [
            "Awa",
            "Mariam",
            "Yao",
            "Kader",
            "Fatou",
            "Aminata",
            "Ibrahim",
            "Sadio",
            "Grace",
            "Jean",
        ]
        motifs = [
            "Fièvre",
            "Douleurs abdominales",
            "Suivi grossesse",
            "Toux persistante",
            "Fatigue",
            "Contrôle",
        ]
        meds = [
            ("Paracétamol 500mg", "1 cp x 3/j", "3 jours"),
            ("Amoxicilline 500mg", "1 gél x 2/j", "5 jours"),
            ("Fer + Acide folique", "1 cp/j", "30 jours"),
        ]

        def rand_phone():
            return "+225" + "".join(str(rng.randint(0, 9)) for _ in range(10))

        def rand_birthdate():
            years_ago = rng.randint(16, 55)
            d = today - timedelta(days=years_ago * 365 + rng.randint(0, 364))
            return date(d.year, d.month, min(d.day, 28))

        def rand_zone():
            return rng.choice(["GRAND_BASSAM", "BONOUA"])

        def rand_sexe():
            return rng.choice(["F", "M"])

        demo_qs = Patient.objects.filter(code_patient__startswith="DEMO-").order_by("id")

        with transaction.atomic():
            if reset:
                Consultation.objects.filter(patient__code_patient__startswith="DEMO-").delete()
                RendezVous.objects.filter(patient__code_patient__startswith="DEMO-").delete()
                SuiviCPN.objects.filter(patient__code_patient__startswith="DEMO-").delete()
                LigneOrdonnance.objects.filter(ordonnance__patient__code_patient__startswith="DEMO-").delete()
                Ordonnance.objects.filter(patient__code_patient__startswith="DEMO-").delete()
                demo_qs.delete()

            existing_demo = list(Patient.objects.filter(code_patient__startswith="DEMO-").order_by("id"))
            patients: list[Patient] = []

            if len(existing_demo) >= n_patients:
                patients = existing_demo[:n_patients]
            else:
                patients = existing_demo[:]
                to_create = n_patients - len(existing_demo)
                start_idx = len(existing_demo) + 1
                for i in range(to_create):
                    idx = start_idx + i
                    nom = rng.choice(noms)
                    prenom = rng.choice(prenoms)
                    code = f"DEMO-{idx:04d}"
                    p, _ = Patient.objects.get_or_create(
                        code_patient=code,
                        defaults={
                            "nom": nom,
                            "prenoms": prenom,
                            "telephone": rand_phone(),
                            "adresse": f"Adresse démo {idx}",
                            "zone": rand_zone(),
                            "sexe": rand_sexe(),
                            "date_naissance": rand_birthdate(),
                            "antecedents": rng.choice(["RAS", "HTA", "Diabète", "Asthme"]),
                        },
                    )
                    patients.append(p)

            created_cpn = 0
            created_rdv = 0
            created_cons = 0
            created_ord = 0

            now = timezone.now()

            for p in patients:
                if p.sexe != "F" and rng.random() < 0.5:
                    pass

                cpn_max = rng.choice([0, 1, 2, 3, 4])
                if p.sexe == "F" and rng.random() < 0.7:
                    cpn_max = max(cpn_max, rng.choice([1, 2, 3, 4]))

                for numero in range(1, cpn_max + 1):
                    if SuiviCPN.objects.filter(patient=p, numero=numero).exists():
                        continue
                    d = today - timedelta(days=rng.randint(15, 250))
                    SuiviCPN.objects.create(patient=p, numero=numero, date=d, notes="")
                    created_cpn += 1

                rdv_count = rng.randint(1, 4)
                for _ in range(rdv_count):
                    delta_days = rng.randint(-40, 30)
                    dt = now + timedelta(days=delta_days, hours=rng.randint(-5, 5))
                    statut = rng.choices(
                        ["PLANIFIE", "EFFECTUE", "ANNULE"],
                        weights=[40, 45, 15],
                        k=1,
                    )[0]
                    RendezVous.objects.create(
                        patient=p,
                        date_heure=dt,
                        objet=rng.choice(["CPN", "Consultation", "Vaccination", "Contrôle"]).strip(),
                        statut=statut,
                    )
                    created_rdv += 1

                cons_count = rng.randint(0, 3)
                for _ in range(cons_count):
                    dt = now - timedelta(days=rng.randint(1, 120), hours=rng.randint(0, 23))
                    Consultation.objects.create(
                        patient=p,
                        date_consultation=dt,
                        motif=rng.choice(motifs),
                        observation="",
                    )
                    created_cons += 1

                if with_ordonnances and rng.random() < 0.6:
                    ord_dt = today - timedelta(days=rng.randint(1, 90))
                    ord_obj = Ordonnance.objects.create(
                        patient=p,
                        date=ord_dt,
                        diagnostic=rng.choice(["Paludisme", "Anémie", "Infection", "" ]),
                        instructions="",
                    )
                    created_ord += 1
                    lignes = rng.randint(1, 3)
                    for _ in range(lignes):
                        med, pos, dur = rng.choice(meds)
                        LigneOrdonnance.objects.create(
                            ordonnance=ord_obj,
                            medicament=med,
                            posologie=pos,
                            duree=dur,
                            commentaire="",
                        )

        self.stdout.write(
            self.style.SUCCESS(
                "Données de démo prêtes. "
                f"patients={len(patients)} cpn_crees={created_cpn} rdv_crees={created_rdv} "
                f"consultations_crees={created_cons} ordonnances_crees={created_ord}"
            )
        )
