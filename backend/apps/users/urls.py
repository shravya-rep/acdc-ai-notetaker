from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("login/", views.auth_login, name="auth-login"),
    path("callback/", views.auth_callback, name="auth-callback"),
    path("me/", views.me, name="auth-me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("preferences/", views.update_preferences, name="update-preferences"),
]
