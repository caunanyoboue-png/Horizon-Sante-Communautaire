from __future__ import annotations

from typing import Any

from django.http import HttpRequest

from .models import AuditLog


def _get_client_ip(request: HttpRequest) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or ""


def log_action(
    request: HttpRequest,
    *,
    action: str,
    instance: Any | None = None,
    app_label: str = "",
    model: str = "",
    object_id: str = "",
    object_repr: str = "",
    extra: dict | None = None,
) -> None:
    if instance is not None:
        app_label = app_label or instance._meta.app_label
        model = model or instance._meta.model_name
        object_id = object_id or str(getattr(instance, "pk", ""))
        object_repr = object_repr or str(instance)

    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

    AuditLog.objects.create(
        user=user,
        action=action,
        app_label=app_label,
        model=model,
        object_id=object_id,
        object_repr=object_repr,
        ip_address=_get_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "") or "")[:255],
        extra=extra or {},
    )
