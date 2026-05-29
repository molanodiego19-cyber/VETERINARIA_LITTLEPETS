from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-e6vi8%$=0pt!plw3mm#cw_4p739re#=7l5!zz$p-l-rz33@l)y'

DEBUG = True

ALLOWED_HOSTS = [
    "veterinaria-littlepets.onrender.com",
    "localhost",
    "127.0.0.1"
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'citas',
    'mascota',
    'veterinarioapp',
    'facturacion',
    'usuarios',
    'panel',
    'notificacion.apps.NotificacionConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    "whitenoise.middleware.WhiteNoiseMiddleware",

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'veterinaria.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'veterinaria.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DATABASE
if os.environ.get("DATABASE_URL"):

    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get("DATABASE_URL")
        )
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'veterinaria',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(
    BASE_DIR,
    'staticfiles'
)

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(
    BASE_DIR,
    'media'
)

# LOGIN
LOGIN_URL = '/usuarios/login/'

# EMAIL
EMAIL_BACKEND = (
    'django.core.mail.backends.smtp.EmailBackend'
)

import os

print("EMAIL_HOST_USER ENV:", os.getenv("EMAIL_HOST_USER"))
print("EMAIL_HOST_PASSWORD ENV:", os.getenv("EMAIL_HOST_PASSWORD"))

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

EMAIL_TIMEOUT = 10