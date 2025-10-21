from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from .views import home_view, about_ahmed_abouzeid_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
	path("admin/", admin.site.urls),
	path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
	path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
	path("users/", include("users.urls")),
	path("accounts/", include("django.contrib.auth.urls")),
	path("requests/", include("requests_app.urls")),
	path("achievements/", include("achievements.urls")),
	path("dashboard/", include("admin_dashboard.urls")),
	path("chat/", include("chat_app.urls")),
	path("about/", about_ahmed_abouzeid_view, name="about_ahmed_abouzeid"),
	path("", home_view, name="home"),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static('/imgs/', document_root=settings.BASE_DIR / 'imgs')

