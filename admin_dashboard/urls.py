from __future__ import annotations

from django.urls import path

from .views import dashboard_view


app_name = "admin_dashboard"

urlpatterns = [
	path("", dashboard_view, name="index"),
]

