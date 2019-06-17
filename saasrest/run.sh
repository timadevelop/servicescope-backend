#!/bin/bash

pip install -r requirements.txt
python manage.py compilemessages -l bg
python manage.py makemigrations saas_core
python manage.py makemigrations authentication
python manage.py makemigrations categories
python manage.py makemigrations locations
python manage.py makemigrations feedback
python manage.py makemigrations messaging
python manage.py makemigrations notifications
python manage.py makemigrations payments
python manage.py makemigrations public_configs
python manage.py makemigrations services
python manage.py makemigrations tags
python manage.py makemigrations votes
python manage.py makemigrations feed
python manage.py makemigrations

python manage.py migrate


if [ "$SAAS_ENV" = "production" ]; then
    echo Production env
    #python manage.py runsslserver --certificate /etc/ssl/certs/fullchain.crt --key /etc/ssl/certs/fullchain.key "0.0.0.0:${PORT}"
    python manage.py runserver "0.0.0.0:${PORT}"
else
    echo Developement env
    python manage.py runserver "0.0.0.0:${PORT}"
fi
