from django.urls import path
from . import views

urlpatterns = [
    path("", views.MeetingListView.as_view(), name="meeting-list"),
    path("<int:pk>/", views.MeetingDetailView.as_view(), name="meeting-detail"),
    path("action-items/", views.ActionItemListView.as_view(), name="action-items"),
    path("action-items/<int:pk>/complete/", views.complete_action_item, name="complete-action-item"),
]
