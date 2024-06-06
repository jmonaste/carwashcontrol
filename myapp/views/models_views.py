from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from ..models import Task
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch





def get_task(request, task_id):
    task = list(Task.objects.filter(id=task_id).values())

    if (len(task)>0):
        data={'message':"Success", 'tarea':task}
    else:
        data={'message':"Not found"}

    return JsonResponse(data)



@login_required
def task_overview(request):
    tasks = Task.objects.all()
    # Recuento por días
    task_counts = tasks.extra({'datecreated': "date(created)"}).values('datecreated').annotate(count=Count('id')).order_by('datecreated')

    task_data = []
    for task in tasks:
        task_data.append({
            'id': task.id,
            'license_plate': task.license_plate,
            'comment': task.comment,
            'license_plate_image': str(task.license_plate_image.url),
            'created': str(task.created),
            'datecompleted': str(task.datecompleted),
            'employee_user_id': task.employee_user_id,
            'img_datetime': str(task.img_datetime),
            'img_lat': task.img_lat,
            'img_long': task.img_long
        })

    task_counts_list = list(task_counts)  # Convert QuerySet to list

    return render(request, 'tasks/task_overview.html', {
        'tasks': tasks,
        'task_data_json': json.dumps(task_data),
        'task_counts': json.dumps(task_counts_list),  # Pass as JSON string
    })












def generate_pdf(request):
    # Crear un objeto HttpResponse con las cabeceras PDF.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="task_list.pdf"'

    # Crear el objeto PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Agregar el logo
    logo_path = "C:\\personal\\4-Proyectos\\00-Jano\\03-ControlNumeroLavados\\djangoproject\\myapp\static\\logo-footer.png"  # Cambia esto por la ruta de tu logo
    elements.append(Image(logo_path, width=2*inch, height=1*inch))

    # Añadir el título del documento
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.alignment = 1
    elements.append(Paragraph("Task List", title_style))

    # Encabezado y pie de página
    def add_header_footer(canvas, doc):
        canvas.saveState()
        header = "Task List"
        footer = "Page %d" % doc.page
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawString(inch, 10.5*inch, header)
        canvas.setFont('Helvetica', 10)
        canvas.drawString(inch, 0.75*inch, footer)
        canvas.restoreState()

    # Añadir los datos de la tabla
    data = [["Patente", "Fecha", "Responsable"]]
    tasks = Task.objects.all()
    for task in tasks:
        formatted_date = task.created.strftime("%d/%m/%Y %H:%M")
        data.append([task.license_plate, formatted_date, task.employee_user_id])

    # Crear la tabla y añadirla al PDF
    table = Table(data, colWidths=[2*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Construir el PDF
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    return response

def download_page(request):
    return render(request, 'tasks/download.html')