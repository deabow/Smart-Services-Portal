from __future__ import annotations

from django.urls import path, include
from .views import router

from .views import request_create_view, request_detail_view, request_list_view


app_name = "requests"

urlpatterns = [
	path("api/", include(router.urls)),
	path("", request_list_view, name="list"),
	path("create/", request_create_view, name="create"),
	path("<str:tracking_number>/", request_detail_view, name="detail"),
]

