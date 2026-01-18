from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from django.forms import inlineformset_factory

from accounts.permissions import role_required

from audit.models import AuditLog
from audit.utils import log_action

from .forms import (
    ConsultationForm,
    LigneOrdonnanceForm,
    OrdonnanceForm,
    PatientForm,
    RendezVousForm,
    SuiviCPNForm,
)
from .models import LigneOrdonnance, Ordonnance, Patient
from .utils import render_to_pdf


def _json_safe(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


@login_required
def patient_list(request):
    q = (request.GET.get("q") or "").strip()
    zone = (request.GET.get("zone") or "").strip()
    sexe = (request.GET.get("sexe") or "").strip()

    qs = Patient.objects.all()
    if q:
        qs = qs.filter(
            Q(code_patient__icontains=q)
            | Q(nom__icontains=q)
            | Q(prenoms__icontains=q)
            | Q(telephone__icontains=q)
        )
    if zone:
        qs = qs.filter(zone=zone)
    if sexe:
        qs = qs.filter(sexe=sexe)

    context = {
        "patients": qs,
        "filters": {"q": q, "zone": zone, "sexe": sexe},
        "kpi_total": Patient.objects.count(),
        "kpi_results": qs.count(),
        "kpi_gb": Patient.objects.filter(zone="GRAND_BASSAM").count(),
        "kpi_bon": Patient.objects.filter(zone="BONOUA").count(),
    }
    return render(request, "patients/patient_list.html", context)


@login_required
def patient_detail(request, pk: int):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, "patients/patient_detail.html", {"patient": patient})


@login_required
@role_required("ADMIN", "MEDECIN", "SAGE_FEMME", "AGENT_COMMUNAUTAIRE")
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=patient)
            return redirect("patient-detail", pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form, "title": "Nouveau patient"})


@login_required
@role_required("ADMIN", "MEDECIN", "SAGE_FEMME")
def patient_update(request, pk: int):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            log_action(request, action=AuditLog.ACTION_UPDATE, instance=patient)
            return redirect("patient-detail", pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, "patients/patient_form.html", {"form": form, "title": "Modifier patient"})


@login_required
@role_required("ADMIN", "MEDECIN", "SAGE_FEMME")
def cpn_create(request, pk: int):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        form = SuiviCPNForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.patient = patient
            suivi.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=suivi, extra={"patient_id": patient.pk})
            return redirect("patient-detail", pk=patient.pk)
    else:
        form = SuiviCPNForm()
    return render(request, "patients/cpn_form.html", {"form": form, "patient": patient})


@login_required
@role_required("ADMIN", "MEDECIN", "SAGE_FEMME", "AGENT_COMMUNAUTAIRE")
def rdv_create(request, pk: int):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.patient = patient
            rdv.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=rdv, extra={"patient_id": patient.pk})
            return redirect("patient-detail", pk=patient.pk)
    else:
        form = RendezVousForm()
    return render(request, "patients/rdv_form.html", {"form": form, "patient": patient})


@login_required
@role_required("ADMIN", "MEDECIN", "SAGE_FEMME")
def consultation_create(request, pk: int):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=consultation, extra={"patient_id": patient.pk})
            return redirect("patient-detail", pk=patient.pk)
    else:
        form = ConsultationForm()
    return render(
        request,
        "patients/consultation_form.html",
        {"form": form, "patient": patient},
    )


@login_required
@role_required("ADMIN", "MEDECIN", "SAGE_FEMME")
def ordonnance_create(request, pk: int):
    patient = get_object_or_404(Patient, pk=pk)

    LigneFormSet = inlineformset_factory(
        Ordonnance,
        LigneOrdonnance,
        form=LigneOrdonnanceForm,
        fields=["medicament", "posologie", "duree", "commentaire"],
        extra=3,
        can_delete=False,
    )

    if request.method == "POST":
        ordonnance_form = OrdonnanceForm(request.POST)
        formset = LigneFormSet(request.POST)
        if ordonnance_form.is_valid() and formset.is_valid():
            ordonnance = ordonnance_form.save(commit=False)
            ordonnance.patient = patient
            ordonnance.save()
            formset.instance = ordonnance
            formset.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=ordonnance, extra={"patient_id": patient.pk})
            return redirect("ordonnance-detail", pk=patient.pk, ordonnance_id=ordonnance.pk)
    else:
        ordonnance_form = OrdonnanceForm()
        formset = LigneFormSet()

    return render(
        request,
        "patients/ordonnance_form.html",
        {"patient": patient, "ordonnance_form": ordonnance_form, "formset": formset},
    )


@login_required
def ordonnance_detail(request, pk: int, ordonnance_id: int):
    patient = get_object_or_404(Patient, pk=pk)
    ordonnance = get_object_or_404(Ordonnance.objects.prefetch_related("lignes"), pk=ordonnance_id, patient=patient)
    return render(
        request,
        "patients/ordonnance_detail.html",
        {"patient": patient, "ordonnance": ordonnance},
    )


@login_required
def ordonnance_pdf(request, pk: int, ordonnance_id: int):
    patient = get_object_or_404(Patient, pk=pk)
    ordonnance = get_object_or_404(Ordonnance.objects.prefetch_related("lignes"), pk=ordonnance_id, patient=patient)
    filename = f"ordonnance_{patient.code_patient}_{ordonnance.date:%Y%m%d}.pdf"
    return render_to_pdf(
        "patients/ordonnance_pdf.html",
        {"patient": patient, "ordonnance": ordonnance},
        filename=filename,
    )


@login_required
@role_required("ADMIN", "MEDECIN")
def patient_export_json(request, pk: int):
    patient = get_object_or_404(Patient, pk=pk)

    ordonnances = (
        patient.ordonnances.prefetch_related("lignes")
        .all()
        .order_by("-date", "-id")
    )

    community_dossiers = (
        patient.dossiers_communautaires.select_related("pathologie")
        .prefetch_related("suivis")
        .all()
        .order_by("-date_diagnostic", "-id")
    )

    payload = {
        "patient": {
            "id": patient.id,
            "code_patient": patient.code_patient,
            "nom": patient.nom,
            "prenoms": patient.prenoms,
            "date_naissance": _json_safe(patient.date_naissance),
            "sexe": patient.sexe,
            "telephone": patient.telephone,
            "adresse": patient.adresse,
            "zone": patient.zone,
            "antecedents": patient.antecedents,
            "created_at": _json_safe(patient.created_at),
            "updated_at": _json_safe(patient.updated_at),
        },
        "cpn": [
            {
                "id": s.id,
                "numero": s.numero,
                "date": _json_safe(s.date),
                "notes": s.notes,
                "created_at": _json_safe(s.created_at),
            }
            for s in patient.suivis_cpn.all().order_by("numero")
        ],
        "rendez_vous": [
            {
                "id": r.id,
                "date_heure": _json_safe(r.date_heure),
                "objet": r.objet,
                "statut": r.statut,
                "created_at": _json_safe(r.created_at),
            }
            for r in patient.rendez_vous.all().order_by("-date_heure")
        ],
        "consultations": [
            {
                "id": c.id,
                "date_consultation": _json_safe(c.date_consultation),
                "motif": c.motif,
                "observation": c.observation,
                "created_at": _json_safe(c.created_at),
            }
            for c in patient.consultations.all().order_by("-date_consultation")
        ],
        "ordonnances": [
            {
                "id": o.id,
                "date": _json_safe(o.date),
                "diagnostic": o.diagnostic,
                "instructions": o.instructions,
                "created_at": _json_safe(o.created_at),
                "lignes": [
                    {
                        "id": l.id,
                        "medicament": l.medicament,
                        "posologie": l.posologie,
                        "duree": l.duree,
                        "commentaire": l.commentaire,
                    }
                    for l in o.lignes.all().order_by("id")
                ],
            }
            for o in ordonnances
        ],
        "community": [
            {
                "id": d.id,
                "pathologie": {
                    "id": d.pathologie_id,
                    "code": d.pathologie.code,
                    "nom": d.pathologie.nom,
                },
                "date_diagnostic": _json_safe(d.date_diagnostic),
                "statut": d.statut,
                "notes": d.notes,
                "created_at": _json_safe(d.created_at),
                "suivis": [
                    {
                        "id": s.id,
                        "date": _json_safe(s.date),
                        "traitement": s.traitement,
                        "observation": s.observation,
                        "created_at": _json_safe(s.created_at),
                    }
                    for s in d.suivis.all().order_by("-date", "-id")
                ],
            }
            for d in community_dossiers
        ],
        "export": {
            "exported_at": _json_safe(timezone.now()),
            "exported_by": getattr(request.user, "username", None),
            "format": "json",
        },
    }

    log_action(
        request,
        action=AuditLog.ACTION_EXPORT,
        instance=patient,
        extra={"format": "json"},
    )

    filename = f"patient_{patient.code_patient}.json"
    response = JsonResponse(payload, json_dumps_params={"ensure_ascii": False})
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
@role_required("ADMIN")
def patient_anonymize(request, pk: int):
    if request.method != "POST":
        return redirect("patient-detail", pk=pk)

    patient = get_object_or_404(Patient, pk=pk)

    original_code = patient.code_patient

    patient.nom = "ANONYMISE"
    patient.prenoms = f"PATIENT_{patient.pk}"
    patient.telephone = ""
    patient.adresse = ""
    patient.antecedents = ""
    patient.date_naissance = None
    patient.save(update_fields=["nom", "prenoms", "telephone", "adresse", "antecedents", "date_naissance", "updated_at"])

    log_action(
        request,
        action=AuditLog.ACTION_UPDATE,
        instance=patient,
        extra={"anonymized": True, "previous_code_patient": original_code},
    )

    return redirect("patient-detail", pk=patient.pk)
