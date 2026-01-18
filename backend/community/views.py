from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required

from audit.models import AuditLog
from audit.utils import log_action

from .forms import DossierCommunautaireForm, SuiviCommunautaireForm
from .models import DossierCommunautaire


@login_required
def dossier_list(request):
    dossiers = DossierCommunautaire.objects.select_related("patient", "pathologie").all()
    return render(request, "community/dossier_list.html", {"dossiers": dossiers})


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
def suivi_create(request, pk: int):
    dossier = get_object_or_404(DossierCommunautaire, pk=pk)
    if request.method == "POST":
        form = SuiviCommunautaireForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.dossier = dossier
            suivi.save()
            log_action(request, action=AuditLog.ACTION_CREATE, instance=suivi, extra={"dossier_id": dossier.pk})
            return redirect("community-dossier-detail", pk=dossier.pk)
    else:
        form = SuiviCommunautaireForm()
    return render(request, "community/suivi_form.html", {"form": form, "dossier": dossier})
