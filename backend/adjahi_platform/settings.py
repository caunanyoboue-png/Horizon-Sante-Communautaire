"""Paramètres Django (base)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Supporte deux layouts:
# - layout "mono" (ancien): templates/ et static/ à la racine
# - layout "split" (recommandé): backend/ (Django) et frontend/ (templates/static) à la racine
REPO_ROOT = BASE_DIR.parent if (BASE_DIR.parent / "frontend").exists() else BASE_DIR

# Charge les variables d'environnement depuis .env si présent
_django_env_already_set = os.getenv("DJANGO_ENV") is not None
load_dotenv(REPO_ROOT / ".env", interpolate=False, override=not _django_env_already_set)

DJANGO_ENV = os.getenv("DJANGO_ENV", "dev").strip().lower()
IS_PROD = DJANGO_ENV in {"prod", "production"}

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is required")

DEBUG = (not IS_PROD) and (os.getenv("DJANGO_DEBUG", "0") == "1")

_allowed_hosts_default = "localhost,127.0.0.1" if DEBUG else ""
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", _allowed_hosts_default).split(",") if h.strip()]

if IS_PROD and not ALLOWED_HOSTS:
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must be set in production")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "patients.apps.PatientsConfig",
    "community.apps.CommunityConfig",
    "reports.apps.ReportsConfig",
    "messaging.apps.MessagingConfig",
    "audit.apps.AuditConfig",
    "api.apps.ApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.AuditMiddleware",
]

ROOT_URLCONF = "adjahi_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            d
            for d in [
                REPO_ROOT / "frontend" / "templates",
                REPO_ROOT / "templates",
            ]
            if d.exists()
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "adjahi_platform.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "adjahi_db"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [
    d
    for d in [
        REPO_ROOT / "frontend" / "static",
        REPO_ROOT / "static",
    ]
    if d.exists()
]

MEDIA_URL = "media/"
MEDIA_ROOT = REPO_ROOT / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

if DEBUG:
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
        "rest_framework.authentication.BasicAuthentication"
    )

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Paramètres sécurité (à renforcer en production)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = os.getenv("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")
SESSION_COOKIE_AGE = int(os.getenv("DJANGO_SESSION_COOKIE_AGE", "3600"))
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "1" if IS_PROD else "0") == "1"
SECURE_HSTS_PRELOAD = os.getenv("DJANGO_SECURE_HSTS_PRELOAD", "1" if IS_PROD else "0") == "1"

SECURE_SSL_REDIRECT = (not DEBUG) and (os.getenv("DJANGO_SECURE_SSL_REDIRECT", "1") == "1")
SESSION_COOKIE_SECURE = (not DEBUG) and (os.getenv("DJANGO_SESSION_COOKIE_SECURE", "1") == "1")
CSRF_COOKIE_SECURE = (not DEBUG) and (os.getenv("DJANGO_CSRF_COOKIE_SECURE", "1") == "1")

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "structured"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}
