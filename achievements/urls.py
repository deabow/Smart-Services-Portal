from __future__ import annotations

from django.urls import path

from .views import achievements_list_view


app_name = "achievements"

urlpatterns = [
	path("", achievements_list_view, name="list"),
]

