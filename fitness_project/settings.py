import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-development-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Dynamic Codespaces configuration
CODESPACE_NAME = os.getenv('CODESPACE_NAME')
CODESPACE_DOMAIN = f"{CODESPACE_NAME}-8000.preview.app.github.dev"  # Updated domain
BASE_URL = f"https://{CODESPACE_DOMAIN}" if CODESPACE_NAME else "http://localhost:8000"

# Security settings
if CODESPACE_NAME:
    ALLOWED_HOSTS = [
        CODESPACE_DOMAIN,
        f'{CODESPACE_NAME}-8000.githubpreview.dev',
        'localhost', 
        '127.0.0.1',
        '.app.github.dev',  # Wildcard for all Codespaces domains
        '.githubpreview.dev'  # Wildcard for all preview domains
    ]
    CSRF_TRUSTED_ORIGINS = [
        BASE_URL,
        f'https://{CODESPACE_NAME}-8000.githubpreview.dev',
        'https://*.preview.app.github.dev',
        'https://*.githubpreview.dev',
        'http://localhost:8000',  # Include localhost for dev consistency
        'http://127.0.0.1:8000'
    ]
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_DOMAIN = None
    SESSION_COOKIE_DOMAIN = None
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'https://localhost:8000',
        'http://127.0.0.1:8000',
        'https://127.0.0.1:8000'
    ]

# Required for admin to work in all environments
USE_X_FORWARDED_HOST = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Cookie settings
CSRF_COOKIE_SECURE = bool(CODESPACE_NAME)  # True in Codespaces, False locally
SESSION_COOKIE_SECURE = bool(CODESPACE_NAME)
CSRF_COOKIE_SAMESITE = 'Lax'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'social_django',
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local
    'booking',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fitness_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'fitness_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'fitness_db'),
        'USER': os.getenv('DB_USER', 'fitness_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 5,
            'sslmode': 'prefer' if CODESPACE_NAME else 'disable',
        },
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = os.getenv('EMAIL_PORT', '587')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Authentication
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login'

# Social Auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_SECRET')
SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('FACEBOOK_OAUTH2_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('FACEBOOK_OAUTH2_SECRET')

# Security Headers
if not DEBUG:
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# Admin Security
ADMIN_URL = os.getenv('ADMIN_URL', 'fitness-admin/')

# Session settings
SESSION_COOKIE_AGE = 3600  # 1 hour session duration
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on activity
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session ends when browser closes
SESSION_COOKIE_SAMESITE = 'Lax'  # Allows top-level redirects

# CSRF settings
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token
CSRF_FAILURE_VIEW = 'booking.views.csrf_failure'