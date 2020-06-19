#!/bin/bash

# pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py compilemessages -l bg
python manage.py makemigrations saas_core authentication categories locations feedback messaging notifications payments public_configs services tags votes feed
python manage.py makemigrations

python manage.py migrate

./configure_api.sh

if [ "$ENV" = "production" ]; then
    echo Production env. Running on port $API_INTERNAL_PORT
    pip install uvicorn gunicorn
    gunicorn saasrest.asgi --bind 0.0.0.0:$API_INTERNAL_PORT -k uvicorn.workers.UvicornWorker --workers 5
else
    echo Development env. Running on port $API_INTERNAL_PORT
    # daphne -b 0.0.0.0 -p ${API_INTERNAL_PORT} saasrest.asgi:application
    python manage.py runserver "0.0.0.0:${API_INTERNAL_PORT}"
fi
