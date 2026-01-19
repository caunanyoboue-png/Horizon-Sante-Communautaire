from django.urls import path

from .views import (
    dashboard,
    home,
    mentions_legales,
    politique_confidentialite,
    partenaires,
)

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("mentions-legales/", mentions_legales, name="mentions-legales"),
    path("politique-confidentialite/", politique_confidentialite, name="politique-confidentialite"),
    path("partenaires/", partenaires, name="partenaires"),
]
