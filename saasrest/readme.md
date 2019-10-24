# Saas rest api


## configuration
See `./saasrest/settings.py`

For google auth: 
0. create Google API Project:
1. Google API key
2. Create a client id
3. enable Google+ API

- `cp local_settings-distrib.py local_settings.py` and edit your settings.

## rest API

- `cd saasrest`
- `source ../venv/bin/activate`
- `pip install -r requirements.txt`
- `alias p3m="python3 manage.py"`
- `p3m makemigrations && p3m migrate && p3m runserver`

## Celery workers:

- `~/.local/bin/celery -A saasrest worker -B --loglevel=info`

###

- collect static on prod