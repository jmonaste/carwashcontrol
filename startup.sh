#!/bin/bin
python manage.py collectstatic && gunicorn --worker 2 mysite.wsgi