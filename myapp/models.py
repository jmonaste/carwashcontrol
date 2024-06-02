from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Task(models.Model):
    license_plate = models.CharField(max_length=100) # vehicle id num - número único de cada vehículo fabricado, por todas las marcas a nivel internacional - regulado por la norma ISO 3833
    comment = models.TextField(blank=True)
    license_plate_image = models.ImageField(upload_to = 'images/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True) # fecha en la que el employee termina el trabajo
    employee_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_user_for_task")

    def __str__(self):
        return self.license_plate