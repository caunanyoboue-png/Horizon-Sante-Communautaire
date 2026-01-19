from django.urls import include, path
from .views import signup_view

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("", include("django.contrib.auth.urls")),
]
