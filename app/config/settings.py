import locale
import logging
import os
import sys
from os.path import join

import requests
from celery.schedules import crontab

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRUE_VALUES = [True, "True", "true", "1"]

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", os.environ.get("SECRET_KEY", os.environ.get("APP_SECRET"))
)

GIT_SHA = os.getenv("GIT_SHA")
DEPLOY_DATE = os.getenv("DEPLOY_DATE", "")
ENVIRONMENT = os.getenv("ENVIRONMENT")
APP_ENV = os.getenv("APP_ENV", "productie")  # acceptatie/test/productie
DEBUG = ENVIRONMENT == "development"

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

USE_TZ = True
TIME_ZONE = "Europe/Amsterdam"
USE_L10N = True
USE_I18N = True
LANGUAGE_CODE = "nl-NL"
LANGUAGES = [("nl", "Dutch")]

DEFAULT_ALLOWED_HOSTS = ".forzamor.nl,localhost,127.0.0.1,.mor.local"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS).split(",")

MELDINGEN_URL = os.getenv("MELDINGEN_URL", "https://mor-core-acc.forzamor.nl")
MELDINGEN_API_URL = os.getenv("MELDINGEN_API_URL", f"{MELDINGEN_URL}/api/v1")
MELDINGEN_API_HEALTH_CHECK_URL = os.getenv(
    "MELDINGEN_API_HEALTH_CHECK_URL", f"{MELDINGEN_URL}/health/"
)
MELDINGEN_TOKEN_API = os.getenv(
    "MELDINGEN_TOKEN_API", f"{MELDINGEN_URL}/api-token-auth/"
)
MELDINGEN_TOKEN_TIMEOUT = 60 * 60
MELDINGEN_USERNAME = os.getenv("MELDINGEN_USERNAME")
MELDINGEN_PASSWORD = os.getenv("MELDINGEN_PASSWORD")

ONDERWERPEN_URL = os.getenv(
    "ONDERWERPEN_URL",
    "https://onderwerpen-acc.forzamor.nl"
    if APP_ENV != "productie"
    else "https://onderwerpen.forzamor.nl",
)

DEV_SOCKET_PORT = os.getenv("DEV_SOCKET_PORT", "9000")

UI_SETTINGS = {"fontsizes": ["fz-medium", "fz-large", "fz-xlarge"]}

INSTALLED_APPS = (
    # templates override
    "apps.health",
    "django.contrib.humanize",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.gis",
    "django.contrib.postgres",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_filters",
    "webpack_loader",
    "corsheaders",
    "ckeditor",
    "ckeditor_uploader",
    "debug_toolbar",
    "mozilla_django_oidc",
    "health_check",
    "health_check.cache",
    "health_check.storage",
    "health_check.db",
    "health_check.contrib.migrations",
    "django_celery_beat",
    "django_celery_results",
    "sorl.thumbnail",
    "django_select2",
    # Apps
    "apps.main",
    "apps.authorisatie",
    "apps.authenticatie",
    "apps.taken",
    "apps.aliassen",
    "apps.rotterdam_formulier_html",
    "apps.context",
    "apps.beheer",
    "apps.release_notes",
    "apps.taaktype",
)

LOGIN_URL = "/login/"

MIDDLEWARE = (
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_session_timeout.middleware.SessionTimeoutMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

# django-permissions-policy settings
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": ["self"],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}

# Database settings
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST_OVERRIDE")
DATABASE_PORT = os.getenv("DATABASE_PORT_OVERRIDE")

DEFAULT_DATABASE = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": DATABASE_NAME,  # noqa:
    "USER": DATABASE_USER,  # noqa
    "PASSWORD": DATABASE_PASSWORD,  # noqa
    "HOST": DATABASE_HOST,  # noqa
    "PORT": DATABASE_PORT,  # noqa
}

DATABASES = {
    "default": DEFAULT_DATABASE,
}
DATABASES.update(
    {
        "alternate": DEFAULT_DATABASE,
    }
    if ENVIRONMENT == "test"
    else {}
)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
AUTH_USER_MODEL = "authenticatie.Gebruiker"

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = "redis://redis:6379/0"

BROKER_URL = CELERY_BROKER_URL
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERYBEAT_SCHEDULE = {
    "queue_every_five_mins": {
        "task": "apps.health.tasks.query_every_five_mins",
        "schedule": crontab(minute=5),
    },
}
CELERY_WORKER_CONCURRENCY = 2
CELERY_WORKER_MAX_TASKS_PER_CHILD = 20
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 200000

SITE_ID = 1
SITE_NAME = os.getenv("SITE_NAME", "FixeR")
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "localhost")

STATICFILES_DIRS = (
    [
        "/app/frontend/public/build/",
    ]
    if DEBUG
    else []
)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "static"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "media"))

ALLOW_UNAUTHORIZED_MEDIA_ACCESS = (
    os.getenv("ALLOW_UNAUTHORIZED_MEDIA_ACCESS", False) in TRUE_VALUES
)
MOR_CORE_URL_PREFIX = "/core"
MOR_CORE_PROTECTED_URL_PREFIX = "/core-protected"

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
        "STATS_FILE": (
            "/static/webpack-stats.json"
            if not DEBUG
            else "/app/frontend/public/build/webpack-stats.json"
        ),
    }
}

# Django REST framework settings
REST_FRAMEWORK = dict(
    PAGE_SIZE=5,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_PAGINATION_CLASS="rest_framework.pagination.LimitOffsetPagination",
    DEFAULT_FILTER_BACKENDS=("django_filters.rest_framework.DjangoFilterBackend",),
    DEFAULT_THROTTLE_RATES={
        "nouser": os.getenv("PUBLIC_THROTTLE_RATE", "60/hour"),
    },
    DEFAULT_PARSER_CLASSES=[
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    DEFAULT_SCHEMA_CLASS="drf_spectacular.openapi.AutoSchema",
    DEFAULT_VERSIONING_CLASS="rest_framework.versioning.NamespaceVersioning",
    DEFAULT_PERMISSION_CLASSES=("rest_framework.permissions.IsAuthenticated",),
    DEFAULT_AUTHENTICATION_CLASSES=(
        "rest_framework.authentication.TokenAuthentication",
    ),
    EXCEPTION_HANDLER="utils.exception_handlers.api_exception_handler",
)


SPECTACULAR_SETTINGS = {
    "TITLE": "FixeR",
    "DESCRIPTION": "Voor het afhandelen van taken voor Meldingen Openbare Ruimte",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
CORS_ORIGIN_WHITELIST = ()
CORS_ORIGIN_ALLOW_ALL = True
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_NAME = "__Secure-sessionid" if not DEBUG else "sessionid"
CSRF_COOKIE_NAME = "__Secure-csrftoken" if not DEBUG else "csrftoken"
SESSION_COOKIE_SAMESITE = "Lax"  # Strict does not work well together with OIDC
CSRF_COOKIE_SAMESITE = "Lax"  # Strict does not work well together with OIDC

# Settings for Content-Security-Policy header
CSP_DEFAULT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_FRAME_SRC = (
    "'self'",
    "iam.forzamor.nl",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    "unpkg.com",
    "cdn.jsdelivr.net",
    "blob:",
)
CSP_IMG_SRC = (
    "'self'",
    "blob:",
    "data:",
    "unpkg.com",
    "service.pdok.nl",
    "mor-core-acc.forzamor.nl",
    "cdn.jsdelivr.net",
    "ows.gis.rotterdam.nl",
    "www.gis.rotterdam.nl",
    # TODO remove picsum.photos
    "picsum.photos",
    "fastly.picsum.photos",
)
CSP_STYLE_SRC = (
    "'self'",
    "data:",
    "'unsafe-inline'",
    "unpkg.com",
    "cdn.jsdelivr.net",
)
CSP_CONNECT_SRC = (
    (
        "'self'",
        "mercure.fixer-test.forzamor.nl",
        "mercure.fixer-acc.forzamor.nl",
        "mercure.fixer.forzamor.nl",
        "cke4.ckeditor.com",
    )
    if not DEBUG
    else (
        "'self'",
        "ws:",
        "localhost:7001",
        "cke4.ckeditor.com",
    )
)
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "config.context_processors.general_settings",
            ],
        },
    }
]

REDIS_URL = "redis://redis:6379"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
    }
}


# Sessions are managed by django-session-timeout-joinup
# Django session settings
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Session settings for django-session-timeout-joinup
SESSION_EXPIRE_MAXIMUM_SECONDS = int(
    os.getenv("SESSION_EXPIRE_MAXIMUM_SECONDS", 60 * 60 * 24 * 7)
)
SESSION_EXPIRE_SECONDS = int(os.getenv("SESSION_EXPIRE_SECONDS", 60 * 60 * 24))
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = int(
    os.getenv("SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD", 60 * 60 * 24)
)
SESSION_CHECK_INTERVAL_SECONDS = int(os.getenv("SESSION_CHECK_INTERVAL_SECONDS", "60"))

THUMBNAIL_BACKEND = "utils.images.ThumbnailBackend"
THUMBNAIL_PREFIX = "afbeeldingen"
THUMBNAIL_KLEIN = "128x128"
THUMBNAIL_STANDAARD = "1480x1480"
BESTANDEN_PREFIX = "bestanden"


def show_debug_toolbar(request):
    return DEBUG and os.getenv("SHOW_DEBUG_TOOLBAR") in TRUE_VALUES


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_debug_toolbar,
    "INSERT_BEFORE": "</head>",
}


LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "verbose",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/app/uwsgi.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "celery": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

OIDC_RP_CLIENT_ID = os.getenv("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.getenv("OIDC_RP_CLIENT_SECRET")

OIDC_REALM = os.getenv("OIDC_REALM")
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL")
OPENID_CONFIG_URI = os.getenv(
    "OPENID_CONFIG_URI",
    f"{AUTH_BASE_URL}/realms/{OIDC_REALM}/.well-known/openid-configuration",
)
OPENID_CONFIG = {}
try:
    OPENID_CONFIG = requests.get(OPENID_CONFIG_URI).json()
except Exception as e:
    logger.error(f"OPENID_CONFIG FOUT, url: {OPENID_CONFIG_URI}, error: {e}")
OIDC_ENABLED = False
if OPENID_CONFIG and OIDC_RP_CLIENT_ID:
    OIDC_ENABLED = True
    OIDC_VERIFY_SSL = os.getenv("OIDC_VERIFY_SSL", True) in TRUE_VALUES
    OIDC_USE_NONCE = os.getenv("OIDC_USE_NONCE", True) in TRUE_VALUES

    OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv(
        "OIDC_OP_AUTHORIZATION_ENDPOINT", OPENID_CONFIG.get("authorization_endpoint")
    )
    OIDC_OP_TOKEN_ENDPOINT = os.getenv(
        "OIDC_OP_TOKEN_ENDPOINT", OPENID_CONFIG.get("token_endpoint")
    )
    OIDC_OP_USER_ENDPOINT = os.getenv(
        "OIDC_OP_USER_ENDPOINT", OPENID_CONFIG.get("userinfo_endpoint")
    )
    OIDC_OP_JWKS_ENDPOINT = os.getenv(
        "OIDC_OP_JWKS_ENDPOINT", OPENID_CONFIG.get("jwks_uri")
    )
    OIDC_RP_SCOPES = os.getenv(
        "OIDC_RP_SCOPES",
        " ".join(OPENID_CONFIG.get("scopes_supported", ["openid", "email", "profile"])),
    )
    OIDC_OP_LOGOUT_ENDPOINT = os.getenv(
        "OIDC_OP_LOGOUT_ENDPOINT",
        OPENID_CONFIG.get("end_session_endpoint"),
    )

    if OIDC_OP_JWKS_ENDPOINT:
        OIDC_RP_SIGN_ALGO = "RS256"

    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "apps.authenticatie.auth.OIDCAuthenticationBackend",
    ]

    ALLOW_LOGOUT_GET_METHOD = True
    OIDC_STORE_ID_TOKEN = True
    OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = int(
        os.getenv("OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS", "300")
    )

    LOGIN_REDIRECT_URL = "/"
    LOGIN_REDIRECT_URL_FAILURE = "/"
    LOGOUT_REDIRECT_URL = OIDC_OP_LOGOUT_ENDPOINT
    LOGIN_URL = "/oidc/authenticate/"


APP_MERCURE_PUBLIC_URL = os.getenv("APP_MERCURE_PUBLIC_URL")
APP_MERCURE_INTERNAL_URL = os.getenv("APP_MERCURE_INTERNAL_URL", APP_MERCURE_PUBLIC_URL)
MERCURE_PUBLISHER_JWT_KEY = os.getenv("MERCURE_PUBLISHER_JWT_KEY")
MERCURE_SUBSCRIBER_JWT_KEY = os.getenv("MERCURE_SUBSCRIBER_JWT_KEY")

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",  # change to Custom if you want the below settings
        # create custom config here: https://ckeditor.com/latest/samples/toolbarconfigurator/index.html#advanced
        "toolbar_Custom": [
            {"name": "basicstyles", "items": ["Bold", "Italic", "Underline", "Strike"]},
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "-",
                    "-",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                    "-",
                ],
            },
            "/",
            {"name": "styles", "items": ["Format", "FontSize"]},
            {"name": "links", "items": ["Link", "Unlink"]},
            {"name": "format", "items": ["CopyFormatting", "RemoveFormat"]},
        ],
        "height": 300,
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"

EMAIL_BEHEER = os.getenv("EMAIL_BEHEER", "ForzaMOR@rotterdam.nl")

SIGNED_DATA_MAX_AGE_SECONDS = int(
    os.getenv("SIGNED_DATA_MAX_AGE_SECONDS", 259200)
)  # 3 days
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "https://web.whatsapp.com/")
