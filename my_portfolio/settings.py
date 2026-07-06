"""
Django settings for my_portfolio project.
Production-ready configuration with Vercel deployment support.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────────────────────
# Read SECRET_KEY from environment variable in production;
# fall back to dev key locally.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-ku)6!xmw*f6(0n390($vk8e-@ls9&o+01lw-wt1@#(n=eu2*y'
)

# DEBUG = False in production (set via env var)
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.vercel.app',          # all *.vercel.app subdomains
    '.now.sh',
    'vasuchauhan.me',       # custom domain (if configured)
    'www.vasuchauhan.me',
]

# ─────────────────────────────────────────────────────────────
# APPLICATION DEFINITION
# ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be right after SecurityMiddleware for static file serving
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_portfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'my_portfolio.wsgi.application'

# ─────────────────────────────────────────────────────────────
# DATABASE
# Uses Neon PostgreSQL in production (via DATABASE_URL env var).
# Falls back to local SQLite for development.
# ─────────────────────────────────────────────────────────────
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://neondb_owner:npg_8MmTj9WhRcdG@ep-curly-art-atp41epa-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require',
        conn_max_age=600,
    )
}

# ─────────────────────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────────────────────
# INTERNATIONALISATION
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────
# STATIC FILES  (WhiteNoise serves them on Vercel)
# ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─────────────────────────────────────────────────────────────
# MEDIA FILES
# Note: Vercel's filesystem is read-only in production.
# Uploaded files (profile images, CV) are committed to the repo
# and served via MEDIA_ROOT. For dynamic uploads in production,
# use Cloudinary or an S3-compatible service.
# ─────────────────────────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ─────────────────────────────────────────────────────────────
# DEFAULT PRIMARY KEY
# ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────────────────────
# GEMINI API KEY  (set as env var in Vercel dashboard)
# ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
