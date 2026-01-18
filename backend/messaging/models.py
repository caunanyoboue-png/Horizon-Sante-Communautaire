from django.conf import settings
from django.db import models


class Thread(models.Model):
    sujet = models.CharField(max_length=255, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="threads")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.sujet or f"Conversation {self.pk}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages_sent")
    contenu = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Message {self.pk}"


class Notification(models.Model):
    TYPE_MESSAGE = "MESSAGE"
    TYPE_URGENCE = "URGENCE"

    TYPE_CHOICES = [
        (TYPE_MESSAGE, "Message"),
        (TYPE_URGENCE, "Alerte urgente"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_MESSAGE)
    titre = models.CharField(max_length=255)
    corps = models.TextField(blank=True)
    url = models.CharField(max_length=255, blank=True)
    lu = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Notif {self.user_id} - {self.type}"
