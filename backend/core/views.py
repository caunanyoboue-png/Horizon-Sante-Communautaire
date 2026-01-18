from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from patients.models import CasSuivi, Consultation, Patient, SuiviCPN


def home(request):
    # Page d'accueil de la plateforme
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
    return render(request, "core/dashboard.html")
