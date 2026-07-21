from pathlib import Path

import environ


# =========================
# BASE DIR
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =========================
# ENVIRONMENT
# =========================

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(
    BASE_DIR.parent / ".env"
)


# =========================
# SECURITY
# =========================

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool(
    "DEBUG",
    default=False,
)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=[],
)


# =========================
# APPLICATIONS
# =========================

INSTALLED_APPS = [
    "daphne",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "channels",

    "comments",
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# URLS
# =========================

ROOT_URLCONF = "config.urls"


# =========================
# TEMPLATES
# =========================

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
            ],
        },
    },
]


# =========================
# WSGI / ASGI
# =========================

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# =========================
# DATABASE
# =========================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env.int(
            "POSTGRES_PORT",
            default=5432,
        ),
    }
}


# =========================
# PASSWORD VALIDATION
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# =========================
# INTERNATIONALIZATION
# =========================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# =========================
# STATIC
# =========================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

# =========================
# MEDIA
# =========================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# =========================
# DEFAULT PRIMARY KEY
# =========================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# =========================
# REST FRAMEWORK
# =========================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication."
        "JWTAuthentication",
    ),

    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),
}


# =========================
# DRF SPECTACULAR
# =========================

SPECTACULAR_SETTINGS = {
    "TITLE": "Comments API",
    "DESCRIPTION": "Comments API documentation",
    "VERSION": "1.0.0",
}


# =========================
# REDIS CACHE
# =========================

CACHES = {
    "default": {
        "BACKEND": (
            "django_redis.cache.RedisCache"
        ),
        "LOCATION": (
            f"redis://"
            f"{env('REDIS_HOST')}:"
            f"{env.int('REDIS_PORT')}/1"
        ),
        "OPTIONS": {
            "CLIENT_CLASS": (
                "django_redis.client.DefaultClient"
            ),
        },
    }
}


# =========================
# CHANNELS
# =========================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": (
            "channels_redis.core."
            "RedisChannelLayer"
        ),
        "CONFIG": {
            "hosts": [
                (
                    env("REDIS_HOST"),
                    env.int("REDIS_PORT"),
                ),
            ],
        },
    },
}


# =========================
# CELERY
# =========================

CELERY_BROKER_URL = (
    f"redis://"
    f"{env('REDIS_HOST')}:"
    f"{env.int('REDIS_PORT')}/2"
)

CELERY_RESULT_BACKEND = (
    f"redis://"
    f"{env('REDIS_HOST')}:"
    f"{env.int('REDIS_PORT')}/2"
)