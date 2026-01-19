from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from patients.models import CasSuivi, Consultation, Patient, SuiviCPN, RendezVous
from community.models import DossierCommunautaire


def home(request):
    context = {
        "kpi_patients": Patient.objects.count(),
        "kpi_consultations": Consultation.objects.count(),
        "kpi_cpn": SuiviCPN.objects.count(),
        "kpi_vih": CasSuivi.objects.filter(type_cas=CasSuivi.TYPE_VIH).count(),
        "kpi_tb": CasSuivi.objects.filter(type_cas=CasSuivi.TYPE_TB).count(),
    }
    return render(request, "core/home.html", context)


@login_required
def dashboard(request):
    profil = getattr(request.user, "profil", None)
    if profil and profil.role == "PATIENT":
        return redirect("patient-portal-home")

    total_patients = Patient.objects.count()
    total_consultations = Consultation.objects.count()
    total_cpn = SuiviCPN.objects.count()

    vih_cases = CasSuivi.objects.filter(type_cas=CasSuivi.TYPE_VIH).count()
    tb_cases = CasSuivi.objects.filter(type_cas=CasSuivi.TYPE_TB).count()

    today = timezone.now().date()
    rdv_today = RendezVous.objects.filter(date_heure__date=today).order_by("date_heure")

    last_week = today - timedelta(days=7)
    recent_consultations = Consultation.objects.filter(date_consultation__gte=last_week).count()

    comm_stats = DossierCommunautaire.objects.values("statut").annotate(count=Count("id"))

    context = {
        "kpi_patients": total_patients,
        "kpi_consultations": total_consultations,
        "kpi_cpn": total_cpn,
        "kpi_vih": vih_cases,
        "kpi_tb": tb_cases,
        "rdv_today": rdv_today,
        "recent_consultations": recent_consultations,
        "comm_stats": comm_stats,
    }

    return render(request, "core/dashboard.html", context)


def mentions_legales(request):
    return render(request, "core/mentions_legales.html")


def politique_confidentialite(request):
    return render(request, "core/politique_confidentialite.html")


def partenaires(request):
    return render(request, "core/partenaires.html")
