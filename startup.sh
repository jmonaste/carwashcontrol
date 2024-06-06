#!/bin/bin
python manage.py collectstatic && gunicorn --workers 2 mysite.wsgi