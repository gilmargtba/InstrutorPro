import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY must be configured")

DEBUG = False
ALLOWED_HOSTS = [item for item in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if item]

INSTALLED_APPS = [
    "apps.core.admin_apps.InstrutorProAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "axes",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "apps.accounts",
    "apps.audit",
    "apps.people",
    "apps.organizations",
    "apps.territories",
    "apps.discovery",
    "apps.marketplace",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.RequestIDMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default="postgis://instrutorpro:instrutorpro@localhost:5432/instrutorpro",
        conn_max_age=60,
        engine="django.contrib.gis.db.backends.postgis",
    )
}

AUTH_USER_MODEL = "accounts.Account"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.stable_exception_handler",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
}
SPECTACULAR_SETTINGS = {
    "TITLE": "InstrutorProCNH API",
    "DESCRIPTION": "Fundação técnica da plataforma nacional da jornada CNH.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300

CORS_ALLOWED_ORIGINS = [item for item in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if item]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_ENABLED = os.getenv("DJANGO_AXES_ENABLED", "true").lower() == "true"
AXES_ONLY_ADMIN_SITE = True
AXES_FAILURE_LIMIT = int(os.getenv("DJANGO_AXES_FAILURE_LIMIT", "5"))
AXES_COOLOFF_TIME = 1
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_SENSITIVE_PARAMETERS = ["password", "otp_token"]

OTP_ADMIN_HIDE_SENSITIVE_DATA = True
ADMIN_MFA_REQUIRED = os.getenv("DJANGO_ADMIN_MFA_REQUIRED", "true").lower() == "true"

# Marketplace M1: recursos reais permanecem deny-by-default. O modo sintético é
# explicitamente separado para demonstração e testes, sem liberar produção real.
SYNTHETIC_MARKETPLACE_ENABLED = (
    os.getenv("SYNTHETIC_MARKETPLACE_ENABLED", "false").lower() == "true"
)
REAL_STUDENT_REGISTRATION_ENABLED = (
    os.getenv("REAL_STUDENT_REGISTRATION_ENABLED", "false").lower() == "true"
)
REAL_INSTRUCTOR_REGISTRATION_ENABLED = (
    os.getenv("REAL_INSTRUCTOR_REGISTRATION_ENABLED", "false").lower() == "true"
)
REAL_INSTRUCTOR_PUBLICATION_ENABLED = (
    os.getenv("REAL_INSTRUCTOR_PUBLICATION_ENABLED", "false").lower() == "true"
)
REAL_STUDENT_DEMAND_ENABLED = os.getenv("REAL_STUDENT_DEMAND_ENABLED", "false").lower() == "true"
PUBLIC_DEMAND_MAP_ENABLED = os.getenv("PUBLIC_DEMAND_MAP_ENABLED", "false").lower() == "true"
DEMAND_MAP_MIN_AGGREGATION_COUNT = int(os.getenv("DEMAND_MAP_MIN_AGGREGATION_COUNT", "0"))

# Dossiê M1: o diretório não é publicado pelo Django/Nginx. A ingestão real segue
# fechada até homologação de storage privado, antimalware e controles LGPD.
MEDIA_ROOT = Path(os.getenv("PRIVATE_DOCUMENT_ROOT", BASE_DIR / "private_documents"))
SYNTHETIC_DOCUMENT_UPLOAD_ENABLED = (
    os.getenv("SYNTHETIC_DOCUMENT_UPLOAD_ENABLED", "false").lower() == "true"
)
REAL_DOCUMENT_UPLOAD_ENABLED = False
INSTRUCTOR_DOCUMENT_MAX_BYTES = int(os.getenv("INSTRUCTOR_DOCUMENT_MAX_BYTES", "5242880"))
