from __future__ import annotations

from django.urls import path

from .views import (
	RegisterView, profile_view, signup_page, logout_view,
	password_reset_request_view, password_reset_admin_view,
	password_reset_admin_handle_view
)


app_name = "users"

urlpatterns = [
	path("register/", RegisterView.as_view(), name="register"),
	path("signup/", signup_page, name="signup"),
	path("profile/", profile_view, name="profile"),
	path("logout/", logout_view, name="logout"),
	path("password-reset-request/", password_reset_request_view, name="password_reset_request"),
	path("admin/password-reset/", password_reset_admin_view, name="password_reset_admin"),
	path("admin/password-reset/<int:request_id>/", password_reset_admin_handle_view, name="password_reset_admin_handle"),
]

