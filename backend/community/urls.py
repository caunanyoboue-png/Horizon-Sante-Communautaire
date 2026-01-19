from django.urls import path

from .views import (
    dossier_create,
    dossier_detail,
    dossier_list,
    dossier_close,
    dossier_update,
    statistiques_pathologies,
    statistiques_zone,
    suivi_create,
)


urlpatterns = [
    path("community/", dossier_list, name="community-dossier-list"),
    path("community/nouveau/", dossier_create, name="community-dossier-create"),
    path("community/<int:pk>/", dossier_detail, name="community-dossier-detail"),
    path("community/<int:pk>/modifier/", dossier_update, name="community-dossier-update"),
    path("community/<int:pk>/cloturer/", dossier_close, name="community-dossier-close"),
    path("community/<int:pk>/suivi/nouveau/", suivi_create, name="community-suivi-create"),
    path("community/statistiques/pathologies/", statistiques_pathologies, name="community-statistiques-pathologies"),
    path("community/statistiques/zones/", statistiques_zone, name="community-statistiques-zone"),
]
