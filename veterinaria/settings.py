from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv


# CARGAR VARIABLES .ENV
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# SEGURIDAD
SECRET_KEY = os.getenv(
"SECRET_KEY",
"django-insecure-e6vi8%$=0pt!plw3mm#cw_4p739re#=7l5!zz$p-l-rz33@l)y"
)

DEBUG = True

ALLOWED_HOSTS = [
"veterinaria-littlepets.onrender.com",
"localhost",
"127.0.0.1",
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

# ==========================

# MIDDLEWARE

# ==========================

MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',


'whitenoise.middleware.WhiteNoiseMiddleware',

'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'veterinaria.urls'

# TEMPLATES
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

# DATABASE
if os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.parse(
            os.getenv("DATABASE_URL"),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "veterinaria",
            "USER": "root",
            "PASSWORD": "root",
            "HOST": "localhost",
            "PORT": "3306",
        }
    }

# ==========================

# PASSWORDS

# ==========================

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

# INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Bogota'

USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# STATIC
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(
BASE_DIR,
'staticfiles'
)

STATICFILES_STORAGE = (
'whitenoise.storage.CompressedManifestStaticFilesStorage'
)

# MEDIA
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(
BASE_DIR,
'media'
)

# LOGIN
LOGIN_URL = '/usuarios/login/'

# EMAIL - BREVO
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

EMAIL_TIMEOUT = 30

import os

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False") == "True"

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True