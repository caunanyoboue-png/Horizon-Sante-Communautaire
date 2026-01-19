from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from accounts.permissions import role_required
from audit.models import AuditLog


@login_required
@role_required("ADMIN")
def audit_log_list(request: HttpRequest) -> HttpResponse:
    logs = AuditLog.objects.select_related("user").all()
    return render(request, "audit/audit_log_list.html", {"logs": logs})


@login_required
@role_required("ADMIN")
def audit_log_export(request: HttpRequest) -> HttpResponse:
    logs = AuditLog.objects.select_related("user").all()

    lines = ["id;date;user;action;app_label;model;object_id;ip_address;user_agent"]
    for log in logs:
        lines.append(
            ";".join(
                [
                    str(log.id),
                    log.created_at.isoformat(),
                    getattr(log.user, "username", "") if log.user_id else "",
                    log.action,
                    log.app_label,
                    log.model,
                    log.object_id,
                    log.ip_address,
                    log.user_agent.replace(";", " "),
                ]
            )
        )

    content = "\n".join(lines)
    response = HttpResponse(content, content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="audit_logs.csv"'
    return response

