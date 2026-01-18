from django.contrib import admin

from .models import Rapport


@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ("type", "created_by", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("type", "created_by__username")
