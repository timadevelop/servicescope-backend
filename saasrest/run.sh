#!/bin/bash

# pip install -r requirements.txt
python manage.py compilemessages -l bg
python manage.py makemigrations saas_core authentication categories locations feedback messaging notifications payments public_configs services tags votes feed
python manage.py makemigrations

python manage.py migrate

if [ "$SAAS_ENV" = "production" ]; then
    echo Production env
    pip install uvicorn gunicorn
    gunicorn saasrest.asgi --bind 0.0.0.0:$PORT -k uvicorn.workers.UvicornWorker --workers 5
    # daphne -b 0.0.0.0 -p ${PORT} saasrest.asgi:application
else
    echo Developement env
    # daphne -b 0.0.0.0 -p ${PORT} saasrest.asgi:application
    python manage.py runserver "0.0.0.0:${PORT}"
fi
