from django.contrib import admin

from .models import Message, Notification, Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "sujet", "created_at")
    search_fields = ("sujet",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "sender", "created_at")
    search_fields = ("contenu", "sender__username")
    list_filter = ("created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "lu", "created_at")
    search_fields = ("titre", "corps", "user__username")
    list_filter = ("type", "lu", "created_at")
