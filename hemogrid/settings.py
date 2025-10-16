from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import os
import cloudinary
import importlib


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
SECRET_KEY = "k8UDe6TdVTtCKCNidxaW7VgKvXu5eMFd6TyH_OXzfznpirN__5aMZr_6oBIN4Y76_iI"
DEBUG = False

_default_allowed_hosts = ".vercel.app,127.0.0.1,localhost,testserver"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", _default_allowed_hosts).split(",")
    if host.strip()
]

# Activation 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')     
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Frontend base URL for email links
FRONTEND_URL = os.getenv('FRONTEND_URL')
EMAIL_VERIFICATION_BASE_URL = os.getenv('EMAIL_VERIFICATION_BASE_URL')

# Application definition

USE_WHITENOISE = False
try:
    importlib.import_module("whitenoise")
    USE_WHITENOISE = True
except ImportError:
    USE_WHITENOISE = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'rest_framework',
    'rest_framework_simplejwt',
    'debug_toolbar',
    'django_filters',
    'corsheaders',
    'accounts',
    'blood_requests',
    'admin_api',
    'notifications',

]

if USE_WHITENOISE:
    INSTALLED_APPS.insert(0, "whitenoise.runserver_nostatic")

AUTH_USER_MODEL = 'accounts.User'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    # Support both legacy 'JWT' and common 'Bearer' prefixes
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
}





MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if USE_WHITENOISE:
    insertion_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1 if 'django.middleware.security.SecurityMiddleware' in MIDDLEWARE else 1
    MIDDLEWARE.insert(insertion_index, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = 'hemogrid.urls'

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

WSGI_APPLICATION = 'hemogrid.wsgi.app'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


_force_sqlite = str(os.getenv('USE_SQLITE_DB', '')).lower() in ('1', 'true', 'yes')
_pg_name = os.getenv('dbname')
_pg_user = os.getenv('user')
_pg_password = os.getenv('password')
_pg_host = os.getenv('host')
_pg_port = os.getenv('port')

if not _force_sqlite and all([_pg_name, _pg_user, _pg_password, _pg_host]):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _pg_name,
            'USER': _pg_user,
            'PASSWORD': _pg_password,
            'HOST': _pg_host,
            'PORT': _pg_port or '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }




# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# Configuration for cloudinary storage      
cloudinary.config(
    cloud_name=os.getenv('cloud_name'),
    api_key=os.getenv('cloudinary_api_key'),
    api_secret=os.getenv('api_secret'),
    secure=True
)

# Media Storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATIC_FILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    '127.0.0.1',
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# If using cookies/auth
CORS_ALLOW_CREDENTIALS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Basic': {
            'type': 'basic'
      },
      'JWT': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Enter your JWT token in the format: `JWT <YOUR_TOKEN>`'
      }
   },
   # Use a defensive generator to avoid 500s during schema build
   'DEFAULT_GENERATOR_CLASS': 'hemogrid.swagger.SafeOpenAPISchemaGenerator',
}
