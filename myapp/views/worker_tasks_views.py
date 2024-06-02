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


# To detect license plates
license_plate_detector = YOLO("C:\\personal\\4-Proyectos\\00-Jano\\03-ControlNumeroLavados\\license_plate_detector.pt") 


@login_required
@allowed_user(allowed_roles=['admin', 'manager', 'employee'])
def tasks(request):

    
    # Obtener la descripción del motivo de rechazo para cada tarea
    return render(request, 'tasks/tasks.html')







@login_required
def task_search(request):
    # filtramos las tareas por usuario, por pendiente y por id (patente)
    query = request.GET.get('q')
    tasks = Task.objects.filter(employee_user=request.user, datecompleted__isnull=True, vin__icontains=query)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })



def upload_image(request, task_id):
    if request.method == 'POST':
        task = Task.objects.get(pk=task_id)
        images = request.FILES.getlist('images')  # Nombre del campo en el formulario
        
        if not images:
            return JsonResponse({'status': 'error', 'message': 'No images uploaded'})

        errors = []
        for image in images:
            image_form = PostImageForm({'task': task.id}, {'images': image})
            if image_form.is_valid():
                post_image = image_form.save(commit=False)
                post_image.task = task
                post_image.save()
            else:
                errors.append(image_form.errors)
        
        if errors:
            return JsonResponse({'status': 'error', 'errors': errors})
        
        return JsonResponse({'status': 'success', 'message': 'Images uploaded successfully'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})





def handle_uploaded_file(f):
    # Ruta donde se guardará la imagen subida
    upload_path = os.path.join('media\images', f.name)
    with open(upload_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return upload_path


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



def register_wash(request):
    if request.method == 'POST':
        form = WashForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['license_plate_photo']
            image_path = handle_uploaded_file(image_file)  # Guardar la imagen subida
            license_plate_text, license_plate_text_score = process_image(image_path)
            
            if license_plate_text:
                return HttpResponse(f'Lavado registrado exitosamente. Matrícula detectada: {license_plate_text}')
            else:
                return HttpResponse('No se pudo detectar la matrícula. Por favor, intente nuevamente.')
    else:
        form = WashForm()
    return render(request, 'register_wash.html', {'form': form})