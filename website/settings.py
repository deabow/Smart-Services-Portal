from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = True
ALLOWED_HOSTS: list[str] = ["*"]


# Applications
INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"rest_framework",
	"rest_framework.authtoken",
	"users",
	"requests_app",
	"achievements",
	"admin_dashboard",
	"chat_app",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
	"website.middleware.VisitorTrackingMiddleware",
	"website.middleware.AdminAccessMiddleware",
]

ROOT_URLCONF = "website.urls"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [BASE_DIR / "templates"],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			],
		},
	}
]

WSGI_APPLICATION = "website.wsgi.application"
ASGI_APPLICATION = "website.asgi.application"


# Database (SQLite for development)
DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": BASE_DIR / "db.sqlite3",
	}
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
	{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
	{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
	{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
	{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "ar"
TIME_ZONE = "Africa/Cairo"
USE_I18N = True
USE_TZ = True


# Static and media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# DRF and JWT
REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": (
		"rest_framework_simplejwt.authentication.JWTAuthentication",
		"rest_framework.authentication.SessionAuthentication",
	),
	"DEFAULT_PERMISSION_CLASSES": (
		"rest_framework.permissions.IsAuthenticatedOrReadOnly",
	),
}

SIMPLE_JWT = {
	"ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
	"REFRESH_TOKEN_LIFETIME": timedelta(days=7),
	"AUTH_HEADER_TYPES": ("Bearer",),
}


# Custom user model
AUTH_USER_MODEL = "users.User"

# Encoding settings
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# CSRF trusted origins for LAN access in development
# Ensures forms/admin work when accessing via http://<LAN-IP>:8000 from other devices
CSRF_TRUSTED_ORIGINS: list[str] = []
_csrf_from_env = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS")
if _csrf_from_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_from_env.split(",") if o.strip()]
else:
    # Always include localhost addresses
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    # Attempt to add the current machine LAN IPv4 automatically
    try:
        import socket

        _local_ip = socket.gethostbyname(socket.gethostname())
        if _local_ip and _local_ip not in ("127.0.0.1", "0.0.0.0"):
            CSRF_TRUSTED_ORIGINS.append(f"http://{_local_ip}:8000")
        
        # Add common local network IPs
        _local_ips = ["192.168.1.6", "192.168.61.1", "192.168.111.1"]
        for ip in _local_ips:
            CSRF_TRUSTED_ORIGINS.append(f"http://{ip}:8000")
    except Exception:
        pass

# Cache configuration for better performance
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default timeout
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Cache settings for static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Image optimization settings
IMAGE_OPTIMIZATION = {
    'QUALITY': 85,
    'MAX_WIDTH': 1200,
    'MAX_HEIGHT': 800,
}

