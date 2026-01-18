from django.urls import path

from .views import dossier_create, dossier_detail, dossier_list, suivi_create

urlpatterns = [
    path("community/", dossier_list, name="community-dossier-list"),
    path("community/nouveau/", dossier_create, name="community-dossier-create"),
    path("community/<int:pk>/", dossier_detail, name="community-dossier-detail"),
    path("community/<int:pk>/suivi/nouveau/", suivi_create, name="community-suivi-create"),
]
