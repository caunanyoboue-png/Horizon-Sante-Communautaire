from django.urls import path

from audit.views import audit_log_export, audit_log_list


urlpatterns = [
    path("audit/logs/", audit_log_list, name="audit-log-list"),
    path("audit/logs/export/", audit_log_export, name="audit-log-export"),
]

