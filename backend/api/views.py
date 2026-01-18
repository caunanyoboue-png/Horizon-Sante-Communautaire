from rest_framework.response import Response
from rest_framework.views import APIView

from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from patients.models import Consultation, Patient, RendezVous, SuiviCPN


class HealthView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        # Endpoint simple pour vérifier que l'API répond
        return Response({"status": "ok"})


class DashboardSummaryView(APIView):
    def get(self, request):
        zone = request.query_params.get("zone")
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        patients_qs = Patient.objects.all()
        if zone:
            patients_qs = patients_qs.filter(zone=zone)

        consultations_qs = Consultation.objects.select_related("patient").all()
        if zone:
            consultations_qs = consultations_qs.filter(patient__zone=zone)
        if start:
            consultations_qs = consultations_qs.filter(date_consultation__date__gte=start)
        if end:
            consultations_qs = consultations_qs.filter(date_consultation__date__lte=end)

        now = timezone.now()
        rdv_24h_qs = RendezVous.objects.select_related("patient").filter(
            statut="PLANIFIE",
            date_heure__gte=now,
            date_heure__lte=now + timedelta(hours=24),
        )
        if zone:
            rdv_24h_qs = rdv_24h_qs.filter(patient__zone=zone)

        cpn_qs = SuiviCPN.objects.select_related("patient").all()
        if zone:
            cpn_qs = cpn_qs.filter(patient__zone=zone)
        if start:
            cpn_qs = cpn_qs.filter(date__gte=start)
        if end:
            cpn_qs = cpn_qs.filter(date__lte=end)

        cpn_counts = {
            1: cpn_qs.filter(numero=1).count(),
            2: cpn_qs.filter(numero=2).count(),
            3: cpn_qs.filter(numero=3).count(),
            4: cpn_qs.filter(numero=4).count(),
        }

        # "Perdues de vue" (règle simple): CPN1 faite, mais pas CPN2 après 60 jours
        cutoff = timezone.localdate() - timedelta(days=60)
        cpn1_old_patient_ids = SuiviCPN.objects.filter(numero=1, date__lte=cutoff).values_list("patient_id", flat=True)
        cpn2_patient_ids = SuiviCPN.objects.filter(numero=2).values_list("patient_id", flat=True)
        perdues_de_vue = Patient.objects.filter(id__in=cpn1_old_patient_ids).exclude(id__in=cpn2_patient_ids)
        if zone:
            perdues_de_vue = perdues_de_vue.filter(zone=zone)

        zones = ["GRAND_BASSAM", "BONOUA"]
        zone_stats = []
        for z in zones:
            zone_stats.append(
                {
                    "zone": z,
                    "patients": Patient.objects.filter(zone=z).count(),
                    "consultations": Consultation.objects.filter(patient__zone=z).count(),
                    "cpn1": SuiviCPN.objects.filter(patient__zone=z, numero=1).count(),
                    "rdv_24h": RendezVous.objects.filter(
                        patient__zone=z,
                        statut="PLANIFIE",
                        date_heure__gte=now,
                        date_heure__lte=now + timedelta(hours=24),
                    ).count(),
                }
            )

        daily = (
            consultations_qs.annotate(day=TruncDate("date_consultation"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        return Response(
            {
                "kpis": {
                    "total_patients": patients_qs.count(),
                    "total_consultations": consultations_qs.count(),
                    "rdv_24h": rdv_24h_qs.count(),
                    "cpn1": cpn_counts[1],
                    "cpn2": cpn_counts[2],
                    "cpn3": cpn_counts[3],
                    "cpn4": cpn_counts[4],
                    "perdues_de_vue": perdues_de_vue.count(),
                },
                "consultations_daily": [{"day": str(x["day"]), "count": x["count"]} for x in daily],
                "zone_stats": zone_stats,
            }
        )
