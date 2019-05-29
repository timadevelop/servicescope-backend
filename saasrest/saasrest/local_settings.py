import os

# google
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '{}'.format(GOOGLE_CLIENT_ID)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '{}'.format(GOOGLE_CLIENT_SECRET)

# SECURITY WARNING: keep the secret key used in production secret!
API_SECRET_KEY = os.environ.get('API_SECRET_KEY')
SECRET_KEY = '{}'.format(API_SECRET_KEY)


API_CLIENT_ID = os.environ.get('API_CLIENT_ID')
API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET')


CELERY_USERNAME = os.environ.get('CELERY_USERNAME')
CELERY_PASSWORD = os.environ.get('CELERY_PASSWORD')

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT')
# Celery
CELERY_BROKER_URL = 'amqp://{}:{}@{}:{}'.format(CELERY_USERNAME, CELERY_PASSWORD, RABBITMQ_HOST, RABBITMQ_PORT)

# redis
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_HOSTS = ['redis://{}:{}'.format(REDIS_HOST, REDIS_PORT)]


STRIPE_LIVE_PUBLIC_KEY = os.environ.get('STRIPE_LIVE_PUBLIC_KEY')
STRIPE_LIVE_SECRET_KEY = os.environ.get('STRIPE_LIVE_SECRET_KEY')
STRIPE_TEST_PUBLIC_KEY = os.environ.get('STRIPE_TEST_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY = os.environ.get('STRIPE_TEST_SECRET_KEY')
STRIPE_WEBHOOK_ENDPOINT_SECRET = os.environ.get('STRIPE_WEBHOOK_ENDPOINT_SECRET')

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
    'HOST': os.environ.get('POSTGRES_HOST'), # set in docker-compose.yml
}

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
