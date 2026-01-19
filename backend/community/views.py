from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required

from audit.models import AuditLog
from audit.utils import log_action
from patients.models import Patient

from .forms import (
    DossierCommunautaireForm,
    HepatiteSuiviForm,
    SanteMentaleSuiviForm,
    SuiviCommunautaireForm,
    TBSuiviForm,
    VIHSuiviForm,
)
from .indicators import get_follow_up_rate, get_lost_to_follow_up, get_pathologie_indicators
from .models import DossierCommunautaire, Pathologie


@login_required
def dossier_list(request):
    pathologie_code = (request.GET.get("pathologie") or "").strip()
    statut = (request.GET.get("statut") or "").strip()
    zone = (request.GET.get("zone") or "").strip()
    date_str = (request.GET.get("date") or "").strip()

    dossiers = DossierCommunautaire.objects.select_related("patient", "pathologie").all()

    if pathologie_code:
        dossiers = dossiers.filter(pathologie__code=pathologie_code)
    if statut:
        dossiers = dossiers.filter(statut=statut)
    if zone:
        dossiers = dossiers.filter(patient__zone=zone)
    if date_str:
        try:
            from datetime import date as _date

            parsed = _date.fromisoformat(date_str)
            dossiers = dossiers.filter(date_diagnostic=parsed)
        except ValueError:
            pass

    pathologies = Pathologie.objects.all()
    statuts = DossierCommunautaire.STATUT_CHOICES
    zones = Patient._meta.get_field("zone").choices

    context = {
        "dossiers": dossiers,
        "pathologies": pathologies,
        "statuts": statuts,
        "zones": zones,
        "filters": {
            "pathologie": pathologie_code,
            "statut": statut,
            "zone": zone,
            "date": date_str,
        },
    }
    return render(request, "community/dossier_list.html", context)


@login_required
def dossier_detail(request, pk: int):
    dossier = get_object_or_404(
        DossierCommunautaire.objects.select_related("patient", "pathologie").prefetch_related("suivis"),
        pk=pk,
    )
    return render(request, "community/dossier_detail.html", {"dossier": dossier})


@login_required
@role_required("ADMIN", "MEDECIN", "PSYCHOLOGUE", "AGENT_COMMUNAUTAIRE")
def dossier_create(request):
    if request.method == "POST":
        form = DossierCommunautaireForm(request.POST)
        if form.is_valid():
            dossier = form.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=dossier)
            return redirect("community-dossier-detail", pk=dossier.pk)
    else:
        form = DossierCommunautaireForm()
    return render(request, "community/dossier_form.html", {"form": form})


@login_required
@role_required("ADMIN", "MEDECIN", "PSYCHOLOGUE", "AGENT_COMMUNAUTAIRE")
def dossier_update(request, pk: int):
    dossier = get_object_or_404(DossierCommunautaire, pk=pk)
    if request.method == "POST":
        form = DossierCommunautaireForm(request.POST, instance=dossier)
        if form.is_valid():
            dossier = form.save()
            log_action(request, action=AuditLog.ACTION_UPDATE, instance=dossier)
            return redirect("community-dossier-detail", pk=dossier.pk)
    else:
        form = DossierCommunautaireForm(instance=dossier)
    return render(request, "community/dossier_form.html", {"form": form})


@login_required
@role_required("ADMIN", "MEDECIN", "PSYCHOLOGUE")
def dossier_close(request, pk: int):
    dossier = get_object_or_404(DossierCommunautaire, pk=pk)
    if request.method == "POST":
        dossier.statut = DossierCommunautaire.STATUT_TERMINE
        dossier.save(update_fields=["statut"])
        log_action(
            request,
            action=AuditLog.ACTION_UPDATE,
            instance=dossier,
            extra={"closed": True},
        )
    return redirect("community-dossier-detail", pk=dossier.pk)


@login_required
@role_required("ADMIN", "MEDECIN", "PSYCHOLOGUE", "AGENT_COMMUNAUTAIRE")
def suivi_create(request, pk: int):
    dossier = get_object_or_404(DossierCommunautaire, pk=pk)

    form_class = SuiviCommunautaireForm
    template_name = "community/suivi_form.html"

    if dossier.pathologie.code == "VIH":
        form_class = VIHSuiviForm
        template_name = "community/vih_suivi_form.html"
    elif dossier.pathologie.code == "TB":
        form_class = TBSuiviForm
        template_name = "community/tb_suivi_form.html"
    elif dossier.pathologie.code == "HEP":
        form_class = HepatiteSuiviForm
    elif dossier.pathologie.code == "SM":
        form_class = SanteMentaleSuiviForm

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.dossier = dossier
            suivi.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=suivi, extra={"dossier_id": dossier.pk})
            return redirect("community-dossier-detail", pk=dossier.pk)
    else:
        form = form_class()
    return render(request, template_name, {"form": form, "dossier": dossier})


@login_required
@role_required("ADMIN", "MEDECIN")
def statistiques_pathologies(request):
    stats = get_pathologie_indicators()
    follow_up_rate = get_follow_up_rate()
    lost_to_follow_up = get_lost_to_follow_up()
    context = {
        "stats": stats,
        "follow_up_rate": follow_up_rate,
        "lost_to_follow_up": lost_to_follow_up,
    }
    return render(request, "community/statistiques.html", context)


@login_required
@role_required("ADMIN", "MEDECIN")
def statistiques_zone(request):
    dossiers = DossierCommunautaire.objects.select_related("patient")

    from django.db.models import Count, Q

    data = (
        dossiers.values("patient__zone")
        .annotate(
            total=Count("id"),
            en_suivi=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_SUIVI)),
            stables=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_STABLE)),
            termines=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_TERMINE)),
            deces=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_DECEDE)),
        )
        .order_by("patient__zone")
    )

    zones = Patient._meta.get_field("zone").choices
    zone_labels = {code: label for code, label in zones}

    enriched = []
    for row in data:
        code = row["patient__zone"]
        enriched.append(
            {
                "zone_code": code,
                "zone_label": zone_labels.get(code, code),
                "total": row["total"],
                "en_suivi": row["en_suivi"],
                "stables": row["stables"],
                "termines": row["termines"],
                "deces": row["deces"],
            }
        )

    return render(request, "community/statistiques_zone.html", {"zones_stats": enriched})
