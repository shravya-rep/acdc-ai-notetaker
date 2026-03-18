from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/meetings/", include("apps.meetings.urls")),
    path("api/graph/", include("apps.graph.urls")),
]
