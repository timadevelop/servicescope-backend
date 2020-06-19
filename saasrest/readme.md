# Saas rest api

Just use my docker configuration.

## rest API

- `cd saasrest`
- `source ../venv/bin/activate`
- `pip install -r requirements.txt`
- `alias p3m="python3 manage.py"`
- `p3m makemigrations && p3m migrate && p3m runserver`

## Celery workers:

- `~/.local/bin/celery -A saasrest worker -B --loglevel=info`
