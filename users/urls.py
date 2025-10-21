from __future__ import annotations

from django.urls import path

from .views import RegisterView, profile_view, signup_page, logout_view


app_name = "users"

urlpatterns = [
	path("register/", RegisterView.as_view(), name="register"),
	path("signup/", signup_page, name="signup"),
	path("profile/", profile_view, name="profile"),
	path("logout/", logout_view, name="logout"),
]

