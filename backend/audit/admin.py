from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "user", "app_label", "model", "object_id", "ip_address")
    list_filter = ("action", "app_label", "model", "created_at")
    search_fields = ("object_id", "object_repr", "user__username", "ip_address")
