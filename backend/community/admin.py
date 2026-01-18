from django.contrib import admin

from .models import DossierCommunautaire, Pathologie, SuiviCommunautaire


class SuiviCommunautaireInline(admin.TabularInline):
    model = SuiviCommunautaire
    extra = 1


@admin.register(Pathologie)
class PathologieAdmin(admin.ModelAdmin):
    list_display = ("code", "nom")
    search_fields = ("code", "nom")


@admin.register(DossierCommunautaire)
class DossierCommunautaireAdmin(admin.ModelAdmin):
    list_display = ("patient", "pathologie", "date_diagnostic", "statut", "created_at")
    search_fields = ("patient__code_patient", "patient__nom", "patient__prenoms", "pathologie__code", "pathologie__nom")
    list_filter = ("pathologie", "statut", "date_diagnostic")
    inlines = [SuiviCommunautaireInline]
