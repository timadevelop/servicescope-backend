#!/bin/bash

pip install -r requirements.txt
python manage.py compilemessages -l bg
python manage.py makemigrations api
python manage.py makemigrations
python manage.py migrate api
python manage.py migrate


if [ "$SAAS_ENV" = "production" ]; then
    echo Production env
    #python manage.py runsslserver --certificate /etc/ssl/certs/fullchain.crt --key /etc/ssl/certs/fullchain.key "0.0.0.0:${PORT}"
    python manage.py runserver "0.0.0.0:${PORT}"
else
    echo Developement env
    python manage.py runserver "0.0.0.0:${PORT}"
fi
