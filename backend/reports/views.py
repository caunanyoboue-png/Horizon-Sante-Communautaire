from __future__ import annotations

from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from accounts.permissions import role_required
from audit.models import AuditLog
from audit.utils import log_action
from patients.models import Consultation, RendezVous, SuiviCPN
from patients.utils import render_to_pdf

from .exports import export_consultations_xlsx, export_patients_xlsx
from .models import Rapport


@login_required
@role_required("ADMIN", "MEDECIN")
def reports_home(request):
    return render(request, "reports/reports_home.html")


@login_required
@role_required("ADMIN", "MEDECIN")
def export_patients(request):
    Rapport.objects.create(type=Rapport.TYPE_PATIENTS_XLSX, created_by=request.user)
    log_action(request, action=AuditLog.ACTION_EXPORT, app_label="reports", model="rapport", object_repr="patients.xlsx")
    content = export_patients_xlsx()
    response = HttpResponse(content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="patients.xlsx"'
    return response


@login_required
@role_required("ADMIN", "MEDECIN")
def export_consultations(request):
    Rapport.objects.create(type=Rapport.TYPE_CONSULTATIONS_XLSX, created_by=request.user)
    log_action(
        request,
        action=AuditLog.ACTION_EXPORT,
        app_label="reports",
        model="rapport",
        object_repr="consultations.xlsx",
    )
    content = export_consultations_xlsx()
    response = HttpResponse(content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="consultations.xlsx"'
    return response


@login_required
@role_required("ADMIN", "MEDECIN")
def rapport_mensuel_pdf(request):
    # Période: mois en cours
    today = date.today()
    month_start = today.replace(day=1)

    consultations = Consultation.objects.filter(date_consultation__date__gte=month_start)
    rdv = RendezVous.objects.filter(date_heure__date__gte=month_start)
    cpn = SuiviCPN.objects.filter(date__gte=month_start)

    Rapport.objects.create(type=Rapport.TYPE_MENSUEL_PDF, created_by=request.user, params={"month_start": str(month_start)})
    log_action(
        request,
        action=AuditLog.ACTION_EXPORT,
        app_label="reports",
        model="rapport",
        object_repr=f"rapport_mensuel_{today:%Y_%m}.pdf",
        extra={"month_start": str(month_start)},
    )

    filename = f"rapport_mensuel_{today:%Y_%m}.pdf"
    return render_to_pdf(
        "reports/rapport_mensuel_pdf.html",
        {
            "month_start": month_start,
            "consultations": consultations.select_related("patient"),
            "rdv": rdv.select_related("patient"),
            "cpn": cpn.select_related("patient"),
        },
        filename=filename,
    )
