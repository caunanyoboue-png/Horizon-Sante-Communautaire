from django.contrib import admin

from .models import CasSuivi, Consultation, LigneOrdonnance, Ordonnance, Patient, RendezVous, SmsLog, SuiviCPN


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("code_patient", "nom", "prenoms", "sexe", "zone", "telephone")
    search_fields = ("code_patient", "nom", "prenoms", "telephone")
    list_filter = ("zone", "sexe")


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("patient", "date_consultation", "motif")
    search_fields = ("patient__code_patient", "patient__nom", "patient__prenoms", "motif")
    list_filter = ("date_consultation",)


@admin.register(SuiviCPN)
class SuiviCPNAdmin(admin.ModelAdmin):
    list_display = ("patient", "numero", "date")
    search_fields = ("patient__code_patient", "patient__nom", "patient__prenoms")
    list_filter = ("numero", "date")


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ("patient", "date_heure", "statut", "objet")
    search_fields = ("patient__code_patient", "patient__nom", "patient__prenoms", "objet")
    list_filter = ("statut", "date_heure")


class LigneOrdonnanceInline(admin.TabularInline):
    model = LigneOrdonnance
    extra = 1


@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ("patient", "date", "diagnostic", "created_at")
    search_fields = ("patient__code_patient", "patient__nom", "patient__prenoms", "diagnostic")
    list_filter = ("date",)
    inlines = [LigneOrdonnanceInline]


@admin.register(SmsLog)
class SmsLogAdmin(admin.ModelAdmin):
    list_display = ("rendez_vous", "telephone", "statut", "provider", "created_at")
    search_fields = ("telephone", "provider", "provider_message_id", "error_message")
    list_filter = ("statut", "provider", "created_at")


@admin.register(CasSuivi)
class CasSuiviAdmin(admin.ModelAdmin):
    list_display = ("patient", "type_cas", "statut", "date_signalement", "created_at")
    search_fields = ("patient__code_patient", "patient__nom", "patient__prenoms")
    list_filter = ("type_cas", "statut", "date_signalement")
