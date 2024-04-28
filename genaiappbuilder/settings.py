"""
Django settings for genaiappbuilder project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from pathlib import Path

import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# False if not in os.environ because of casting above
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRETKEY')

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    "core.apps.CoreConfig",
    "genai_app.apps.GenaiAppConfig",
    # 3rd party apps
    "daphne",
    "redisboard",
    "debug_toolbar",
    "taggit",
    "compressor",
    "modelcluster",
    "widget_tweaks",
    "analytical",
    "tailwind",
    "django_browser_reload",
    "tinymce",
    "auditlog",
    # auth
    'allauth',
    'allauth.account',
    'allauth.mfa',
    'allauth.socialaccount',
    'allauth_ui',
    'allauth.socialaccount.providers.google',
    # wagtail apps
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtailimporter",
    # django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "genaiappbuilder.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "genaiappbuilder.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('PGDATABASE'),
        'USER': env('PGUSER'),
        'PASSWORD': env('PGPASSWORD'),
        'HOST': env('PGHOST'),
        'PORT': env('PGPORT'),
        # Enable persistent connections, but close them if they're
        # idle for more than 30 seconds
        'CONN_MAX_AGE': int(env('PGCONN_MAX_AGE')),
        'OPTIONS': {
            'sslmode': env('PGSSLMODE'),
        }
    },
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_USER_MODEL = "core.CustomUser"
SITE_ID = 1
LOGIN_REDIRECT_URL = '/'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
MFA_ADAPTER = "allauth.mfa.adapter.DefaultMFAAdapter"

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('ALLAUTH_GOOGLE_CLIENT_ID'),
            'secret': env('ALLAUTH_GOOGLE_SECRET'),
            'key': '123'
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# compressor
COMPRESS_ROOT = BASE_DIR / 'static'
COMPRESS_ENABLED = True
STATICFILES_FINDERS = (
    'compressor.finders.CompressorFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# wagtail
WAGTAIL_SITE_NAME = 'My Example Site'
WAGTAILADMIN_BASE_URL = 'http://127.0.0.1'
WAGTAILTRANSFER_SOURCES = {
    'remotedev': {
        'BASE_URL': 'http://3.70.177.68:8000/wagtail-transfer/',
        'SECRET_KEY': env('REMOTEDEV_WAGTAIL_SECRET_KEY'),
    },
}

WAGTAILTRANSFER_SECRET_KEY = env('LOCAL_WAGTAIL_SECRET_KEY')
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# daphne async
ASGI_APPLICATION = "genaiappbuilder.asgi.application"

# caches
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{env('REDISUSER')}@{env('REDISHOST')}:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": env('REDISPASSWORD')
        }
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

AWS_REGION = env('AWS_REGION')
AWS_DYNAMODB_HOST = env('AWS_DYNAMODB_HOST', default=None)

INTERNAL_IPS = [
    '109.58.234.109'
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_LOG_LEVEL = 'INFO'
CELERY_WORKER_LOG_FORMAT = '[%(levelname)s/%(processName)s] (%(module)s.%(funcName)s): %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(levelname)s/%(processName)s] %(task_name)s[%(task_id)s]: %(message)s'
# LiteLLM
LITE_LLM_API_KEY = env('LITE_LLM_API_KEY')
LITE_LLL_BASE_URL = env('LITE_LLL_BASE_URL')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('{levelname} {asctime} {module} '
                       '{process:d} {thread:d} {message}'),
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
