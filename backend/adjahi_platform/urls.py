"""Routes URL globales."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("patients.urls")),
    path("", include("community.urls")),
    path("", include("reports.urls")),
    path("", include("messaging.urls")),
    path("accounts/", include("accounts.urls")),
    path("api/", include("api.urls")),
]
