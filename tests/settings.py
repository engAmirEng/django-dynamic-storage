import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

import environ


BASE_DIR = Path(__file__).resolve().parent
env = environ.Env(JUST_POSTGRES=(bool, False), DATABASE_URL=(str, "sqlite://:memory:"))

# Take environment variables from .env file if exists
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


SECRET_KEY = "django-insecure--5frsp!e=r&8bu^p2%)iie!*95keawjm*+7hu*8pk5=cop&+e!"

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    "django.contrib.admin.apps.AdminConfig",
    "django.contrib.auth.apps.AuthConfig",
    "django.contrib.contenttypes.apps.ContentTypesConfig",
    "django.contrib.sessions.apps.SessionsConfig",
    "django.contrib.messages.apps.MessagesConfig",
    "django.contrib.staticfiles.apps.StaticFilesConfig",
    "testapp.apps.TestAppConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"


DATABASES = {"default": env.db_url("DATABASE_URL")}
if (
    env.bool("JUST_POSTGRES")
    and DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql"
):
    raise ImproperlyConfigured(
        f"`JUST_POSTGRES` is set but engin is {DATABASES['default']['ENGINE']}"
    )

AUTH_USER_MODEL = "testapp.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
