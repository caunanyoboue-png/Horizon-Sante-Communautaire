from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from audit.models import AuditLog
from audit.utils import log_action
from patients.models import Patient


class AuditMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return response

        path = request.path or ""

        if path.startswith("/static/"):
            return response

        log_action(
            request,
            action=AuditLog.ACTION_ACCESS,
            extra={
                "path": path,
                "method": request.method,
                "status_code": response.status_code,
            },
        )

        if path.startswith("/patients/"):
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 2 and parts[0] == "patients":
                pk_str = parts[1]
                if pk_str.isdigit():
                    try:
                        patient = Patient.objects.get(pk=int(pk_str))
                        Patient.objects.filter(pk=patient.pk).update(date_dernier_acces=timezone.now())
                    except Patient.DoesNotExist:
                        pass

        return response

