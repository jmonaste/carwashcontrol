from django import forms
from django.forms import ModelForm
from .models import Task

class createNewTask(forms.Form):
    vin = forms.CharField(label='Titulo de tarea', max_length=200, widget=forms.TextInput(attrs={'class': 'input'}))
    description = forms.CharField(label="Descipcion de la tarea", widget=forms.Textarea(attrs={'class': 'input'})) 




class WashForm(forms.Form):
    license_plate_photo = forms.ImageField(label='Foto de la Matrícula')
