from django.urls import path
from . import views

urlpatterns = [
    path("webhook/", views.webhook_endpoint, name="graph-webhook"),
]
