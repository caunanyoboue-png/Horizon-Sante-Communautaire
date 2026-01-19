from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Count, Max, Q
from django.utils import timezone

from .models import DossierCommunautaire


def get_pathologie_indicators() -> list[dict[str, Any]]:
    qs = (
        DossierCommunautaire.objects.select_related("pathologie")
        .values("pathologie_id", "pathologie__code", "pathologie__nom")
        .annotate(
            total=Count("id"),
            en_suivi=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_SUIVI)),
            stables=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_STABLE)),
            termines=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_TERMINE)),
            deces=Count("id", filter=Q(statut=DossierCommunautaire.STATUT_DECEDE)),
        )
        .order_by("pathologie__nom")
    )
    return list(qs)


def get_follow_up_rate() -> float:
    total = DossierCommunautaire.objects.count()
    if total == 0:
        return 0.0
    with_suivi = (
        DossierCommunautaire.objects.filter(suivis__isnull=False)
        .distinct()
        .count()
    )
    return with_suivi / float(total)


def get_lost_to_follow_up(days: int = 90) -> int:
    today = timezone.now().date()
    threshold = today - timedelta(days=days)

    qs = (
        DossierCommunautaire.objects.filter(statut=DossierCommunautaire.STATUT_SUIVI)
        .annotate(last_suivi=Max("suivis__date"))
        .filter(
            Q(last_suivi__lt=threshold)
            | Q(last_suivi__isnull=True, date_diagnostic__lt=threshold)
        )
    )
    return qs.count()

