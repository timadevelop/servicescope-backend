"""
Django settings for saasrest project.
"""

from corsheaders.defaults import default_headers
import os
import saasrest.settings.local_settings as local_settings
from .local_settings import *  # noqa
from .auth import *  # noqa
from .apps import *  # noqa
from .rest import *  # noqa

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# urls
ROOT_URLCONF = 'saasrest.urls'
# wsgi/asgi
WSGI_APPLICATION = 'saasrest.wsgi.application'
ASGI_APPLICATION = 'saasrest.asgi.application'

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

if local_settings.DEBUG:
    from .debug import *


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

# NOTE: Static files should be served using nginx/apache behind cloudflare/cloudfront
STATIC_URL = local_settings.STATIC_URL
STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Media files
if local_settings.USE_S3:
    # aws settings
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'saasrest.settings.storage_backends.PublicMediaStorage'
else:
    # NOTE: Media files should be served on services like Amazon S3
    # DO NOT keep media and any user files inside docker volumes.
    MEDIA_URL = local_settings.DEV_MEDIA_URL
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# CELERY_TIMEZONE = 'UTC'
# CELERY_ENABLE_UTC = True
# CELERY_TIMEZONE = 'Europe/Sofia'

# Middlewares
MIDDLEWARE = [
    # cache
    # 'django.middleware.cache.UpdateCacheMiddleware',
    #
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # for admin panel reasons
    'django.contrib.messages.middleware.MessageMiddleware',
    # clickjacking
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # cache
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]

if local_settings.DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# TODO: check cookie age
DAYS = 30 * 4
SESSION_COOKIE_AGE = 60 * 60 * 24 * DAYS

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    WEBCLIENT_PUBLIC_URL
]

# API keys configuration
API_KEY_CUSTOM_HEADER = "HTTP_API_KEY"
CORS_ALLOW_HEADERS = list(default_headers) + [
    'Api-Key',
]


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        # root logger
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        #
        'saasrest': {
            'level': local_settings.DJANGO_LOG_LEVEL,
            'handlers': ['console'],
            # required to avoid double logging with root logger
            'propagate': False,
        },
    },
}

# dj templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '',
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # OAuth
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

# Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": local_settings.REDIS_HOSTS,
        },
    },
}

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': local_settings.MEMCACHED_LOCATION,
    }
}

# Key in `CACHES` dict
CACHE_MIDDLEWARE_ALIAS = 'default'

# Additional prefix for cache keys
CACHE_MIDDLEWARE_KEY_PREFIX = ''

# Cache key TTL in seconds
CACHE_MIDDLEWARE_SECONDS = 600


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

# use Accept-Language Header (i.e. 'ru-ru', 'es-es', 'en-US', 'bg')
LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'Europe/Sofia'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

# Emails
EMAIL_USE_TLS = True
EMAIL_HOST = local_settings.EMAIL_HOST
EMAIL_PORT = local_settings.EMAIL_PORT
DEFAULT_FROM_EMAIL = local_settings.EMAIL_HOST_USER
EMAIL_HOST_USER = local_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD
