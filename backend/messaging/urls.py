from django.urls import path

from .views import notifications_list, thread_create, thread_detail, thread_list

urlpatterns = [
    path("messages/", thread_list, name="messaging-thread-list"),
    path("messages/nouveau/", thread_create, name="messaging-thread-create"),
    path("messages/<int:pk>/", thread_detail, name="messaging-thread-detail"),
    path("notifications/", notifications_list, name="messaging-notifications"),
]
