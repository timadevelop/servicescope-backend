import os

ENV = os.environ.get('ENV', 'development')

DEBUG = True
if ENV == 'production':
    DEBUG = False

#
#
#

API_PUBLIC_HOST = os.environ.get('API_PUBLIC_HOST')
API_PUBLIC_PORT = os.environ.get('API_PUBLIC_PORT')
API_PUBLIC_URL = os.environ.get('API_PUBLIC_URL')

ALLOWED_HOSTS = os.environ.get('API_ALLOWED_HOSTS').split(',')
ALLOWED_HOSTS = ['192.168.1.22', 'localhost', '127.0.0.1'] + ALLOWED_HOSTS
INTERNAL_IPS = ['192.168.1.22', 'localhost', '127.0.0.1']

WEBCLIENT_PUBLIC_URL = os.environ.get('WEBCLIENT_PUBLIC_URL')

#
# general
#

DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO')
SITE_ID = os.environ.get('SITE_ID', 1)
SITE_NAME = os.environ.get('SITE_NAME', 'Serviscope.bg')

#
# google
#
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

#
# Facebook
#
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')

# Facebook Ads

# https://business.facebook.com/settings/system-users/<userid>/?business_id=<Your business id>
# page acccess token (page_mmanage, publish_page, ads_manage, ....)
FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
# https://business.facebook.com/settings/ad-accounts/<FACEBOOK_AD_ACCOUNT_ID>?business_id=<Your business id>
FACEBOOK_AD_ACCOUNT_ID = os.environ.get('FACEBOOK_AD_ACCOUNT_ID')
# <page url>/about
FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')

# SECURITY WARNING: keep the secret key used in production secret!
API_SECRET_KEY = os.environ.get('API_SECRET_KEY')
SECRET_KEY = '{}'.format(API_SECRET_KEY)


API_CLIENT_ID = os.environ.get('API_CLIENT_ID')
API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET')


# CELERY_USERNAME = os.environ.get('CELERY_USERNAME')
# CELERY_PASSWORD = os.environ.get('CELERY_PASSWORD')
#
# RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
# RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
# # Celery
# CELERY_BROKER_URL = 'amqp://{}:{}@{}:{}'.format(CELERY_USERNAME, CELERY_PASSWORD, RABBITMQ_HOST, RABBITMQ_PORT)

# redis
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_HOSTS = ['redis://{}:{}'.format(REDIS_HOST, REDIS_PORT)]

STRIPE_LIVE_PUBLIC_KEY = os.environ.get('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_LIVE_SECRET_KEY = os.environ.get('STRIPE_LIVE_SECRET_KEY')
STRIPE_TEST_PUBLIC_KEY = os.environ.get('STRIPE_TEST_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY = os.environ.get('STRIPE_TEST_SECRET_KEY')
STRIPE_WEBHOOK_ENDPOINT_SECRET = os.environ.get(
    'STRIPE_WEBHOOK_ENDPOINT_SECRET')

STRIPE_LIVE_MODE = os.environ.get('STRIPE_LIVE_MODE')
if STRIPE_LIVE_MODE == 'True':
    STRIPE_LIVE_MODE = True
else:
    STRIPE_LIVE_MODE = False

# print('db port {}'.format(os.environ.get('POSTGRES_PORT')))
# DATABASE
DB_CONFIG = {
    'NAME': 'postgres',
    'USER': 'postgres',
    'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
    'PORT': os.environ.get('POSTGRES_PORT'),
    'HOST': os.environ.get('POSTGRES_HOST'),  # set in docker-compose.yml
}

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.zoho.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Cache
MEMCACHED_LOCATION = os.environ.get('MEMCACHED_LOCATION')

# S3

USE_S3 = os.getenv('USE_S3', 'FALSE')
