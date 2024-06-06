#!/bin/sh

# Configuraciones iniciales
python manage.py migrate
# Cualquier otro comando de configuración necesario

# Iniciar el servidor Django
python manage.py runserver 0.0.0.0:8000
