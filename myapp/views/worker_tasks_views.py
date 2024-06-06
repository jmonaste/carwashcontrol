from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from ..models import Task
from ..forms import createNewTask, WashForm
from ..decorators import unauthenticated_user, allowed_user
from ..utils import read_license_plate
from django.db import IntegrityError, connection
import plotly.express as px
import numpy as np
from ultralytics import YOLO
import cv2
import os
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import Task
from django.contrib.auth.models import User
import json
from datetime import datetime
from django.conf import settings
from django.templatetags.static import static
import piexif
from PIL import Image
from PIL import Image
import exifread
import folium
import matplotlib.pyplot as plt
import numpy as np
import webbrowser


# To detect license plates
license_plate_detector = YOLO("C:\\personal\\4-Proyectos\\00-Jano\\03-ControlNumeroLavados\\license_plate_detector.pt") 




def parse_gps_coordinate(coord):
    # Convierte una cadena del tipo '[40, 25, 3347/100]' en una lista de números
    coord = coord.strip('[]')
    parts = coord.split(', ')
    return [int(parts[0]), int(parts[1]), float(parts[2].split('/')[0]) / float(parts[2].split('/')[1])]

def convert_to_degress(value):
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1]
    s = value[2][0] / value[2][1]

    return d + (m / 60.0) + (s / 3600.0)

def get_exif_data(image_path):
    exif_data = {
        "datetime": None,
        "latitude": None,
        "longitude": None,
    }
    try:
        img = Image.open(image_path)
        exif_dict = piexif.load(img.info['exif'])
        
        # Fecha y hora
        if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
            exif_data["datetime"] = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        
        # Geolocalización
        gps_info = exif_dict.get('GPS', {})
        if gps_info:
            lat = gps_info.get(piexif.GPSIFD.GPSLatitude)
            lat_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef)
            lon = gps_info.get(piexif.GPSIFD.GPSLongitude)
            lon_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef)

            if lat and lat_ref and lon and lon_ref:
                exif_data["latitude"] = convert_to_degress(lat) * (1 if lat_ref == b'N' else -1)
                exif_data["longitude"] = convert_to_degress(lon) * (1 if lon_ref == b'E' else -1)
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")

    return exif_data

def get_exif_data_from_file(f):
    exif_data = {
        "datetime": None,
        "latitude": None,
        "longitude": None,
    }
    try:
        img = Image.open(f)
        exif_dict = piexif.load(img.info['exif'])

        # Fecha y hora
        if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
            exif_data["datetime"] = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
        
        # Geolocalización
        gps_info = exif_dict.get('GPS', {})
        if gps_info:
            lat = gps_info.get(piexif.GPSIFD.GPSLatitude)
            lat_ref = gps_info.get(piexif.GPSIFD.GPSLatitudeRef)
            lon = gps_info.get(piexif.GPSIFD.GPSLongitude)
            lon_ref = gps_info.get(piexif.GPSIFD.GPSLongitudeRef)

            if lat and lat_ref and lon and lon_ref:
                exif_data["latitude"] = convert_to_degress(lat) * (1 if lat_ref == b'N' else -1)
                exif_data["longitude"] = convert_to_degress(lon) * (1 if lon_ref == b'E' else -1)
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")

    return exif_data


def get_decimal_degrees(coord):
    return coord[0] + coord[1] / 60 + coord[2] / 3600

def create_map(lat, long):
    # Crea un mapa centrado en las coordenadas
    mapa = folium.Map(location=[lat, long], zoom_start=15)
    
    # Añade un marcador en las coordenadas
    folium.Marker(location=[lat, long], popup="Ubicación").add_to(mapa)
    
    # Guarda el mapa como un archivo HTML
    mapa.save("mapa.html")
    
    # Abre el mapa en el navegador
    webbrowser.open("mapa.html")

from datetime import datetime

def convert_datetime_format(exif_datetime):
    """
    Convierte una fecha y hora en formato EXIF (YYYY:MM:DD HH:MM:SS)
    a un formato aceptado por Django (YYYY-MM-DD HH:MM:SS).
    """
    try:
        # Convertir la cadena de fecha y hora de EXIF a un objeto datetime
        dt = datetime.strptime(exif_datetime, "%Y:%m:%d %H:%M:%S")
        # Convertir el objeto datetime a una cadena en el formato aceptado por Django
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Error al convertir el formato de fecha y hora: {e}")
        return None




@login_required
@allowed_user(allowed_roles=['admin', 'manager', 'employee'])
def tasks(request):
    return render(request, 'tasks/tasks.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def task_search(request):
    # filtramos las tareas por usuario, por pendiente y por id (patente)
    query = request.GET.get('q')
    tasks = Task.objects.filter(employee_user=request.user, datecompleted__isnull=True, vin__icontains=query)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })

def handle_uploaded_file(f):
    upload_dir = settings.MEDIA_ROOT
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def process_image(image_path):
    # Leer la imagen
    frame = cv2.imread(image_path)

    # Detectar matrículas
    license_plates = license_plate_detector(frame)[0]
    print('se prodece a leer')

    # Recortar la matrícula --> no se recorta se procesa la imagen entera
    license_plate_crop = frame

    # Procesar la matrícula
    license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
    _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

    # Leer el número de la matrícula
    license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

    print('license_plate_text')

    if license_plate_text is not None:
        return license_plate_text, license_plate_text_score

    return None, None





@csrf_exempt
@login_required
def create_task(request):
    if request.method == 'POST' and is_ajax(request):
        data = json.loads(request.body)
        license_plate = data.get('license_plate')

        # Retrieve uploaded image path from session
        uploaded_image = request.session.get('uploaded_image_path')

        # Obtén los metadatos EXIF
        license_plate_img_datetime = data.get('imgDatetime')
        license_plate_img_lat = data.get('imgLat')
        license_plate_img_long = data.get('imgLong')

        if license_plate and uploaded_image and request.user.is_authenticated:
            task = Task.objects.create(
                license_plate=license_plate,
                comment="generado automáticamente",
                license_plate_image=uploaded_image,
                created=datetime.now(),
                datecompleted=datetime.now(),
                employee_user=request.user,
                img_datetime=convert_datetime_format(license_plate_img_datetime),
                img_lat=license_plate_img_lat,
                img_long=license_plate_img_long,

            )
            return JsonResponse({'success': True, 'task_id': task.id})
        else:
            return JsonResponse({'success': False, 'error': 'Datos inválidos o usuario no autenticado.'})

    return JsonResponse({'success': False, 'error': 'Solicitud inválida.'})


@login_required
@csrf_exempt
def register_wash(request):
    if request.method == 'POST' and is_ajax(request):
        image_file = request.FILES['license_plate_photo']
        
        # Leer los metadatos EXIF directamente del archivo recibido
        exif_data = get_exif_data_from_file(image_file)
        print(exif_data)

        # Guardar la imagen en el servidor
        image_path = handle_uploaded_file(image_file)
        
        # Procesar la imagen
        license_plate_text, license_plate_text_score = process_image(image_path)

        if license_plate_text:
            # Guardar la ruta de la imagen en la sesión
            request.session['uploaded_image_path'] = image_path

            return JsonResponse({
                'success': True, 
                'license_plate_text': license_plate_text, 
                'image_url': request.build_absolute_uri(settings.MEDIA_URL + os.path.basename(image_path)),
                'exif_data': exif_data
            })
        else:
            return JsonResponse({'success': False, 'error': 'No se pudo detectar la matrícula.'})

    return JsonResponse({'success': False, 'error': 'Solicitud inválida.'})
