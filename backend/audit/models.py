from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_EXPORT = "EXPORT"
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"

    ACTION_CHOICES = [
        (ACTION_CREATE, "CREATE"),
        (ACTION_UPDATE, "UPDATE"),
        (ACTION_DELETE, "DELETE"),
        (ACTION_EXPORT, "EXPORT"),
        (ACTION_LOGIN, "LOGIN"),
        (ACTION_LOGOUT, "LOGOUT"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    app_label = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    object_id = models.CharField(max_length=64, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)

    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    extra = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} - {self.action} - {self.app_label}.{self.model} {self.object_id}"
