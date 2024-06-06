from django.shortcuts import render
from ..models import Task
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from ..decorators import unauthenticated_user, allowed_user


# Create your views here.


#region vistas generales

def index(request):
    return render(request, 'global/index.html')

def about(request):
    return render(request, 'global/about.html')

@unauthenticated_user
def signup(request):
    if request.method == 'GET':
        return render(request, 'global/signup.html', {"form": UserCreationForm})
    else:

        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('index')
            except IntegrityError:
                return render(request, 'global/signup.html', {"form": UserCreationForm, "error": "Username already exists."})

        return render(request, 'global/signup.html', {"form": UserCreationForm, "error": "Passwords did not match."})

@unauthenticated_user
def signin(request):
    if request.method == 'GET':
        return render(request, 'global/signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'global/signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        return redirect('index')
    
@allowed_user(allowed_roles=['admin', 'manager', 'employee', 'customer'])
def signout(request):
    logout(request)
    return redirect('index')



# VISTAS TAREAS --------------------------------------------------------------------------------------------

#region Employee

@login_required
def task_search(request):
    # filtramos las tareas por usuario, por pendiente y por id (patente)
    query = request.GET.get('q')
    tasks = Task.objects.filter(employee_user=request.user, datecompleted__isnull=True, vin__icontains=query)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })




#endregion

@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def tasks_client_pending(request):
    # fecha de compeltada, y manager rellena, cliente vacía
    tasks = Task.objects.filter(datecompleted__isnull=False, datecompleted_manager_approval__isnull=False, datecompleted_client_approval__isnull=True)

    return render(request, 'tasks/tasks_client_pending.html', {
        'tasks': tasks
    })

@login_required
@allowed_user(allowed_roles=['admin', 'manager', 'customer'])
def tasks_completed(request):
    # filtramos las tareas por usuario
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    #tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })


@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def tasks_history(request):
    tasks = Task.objects.all() # todas las tareas
    return render(request, 'tasks/tasks_history.html', {
        'tasks': tasks
    })


@login_required
@allowed_user(allowed_roles=['admin', 'manager'])
def task_manager_pending(request):
    # Mostrar todas las tareas entregadas por employee, independientemente del usuario
    tasks = Task.objects.filter(datecompleted__isnull=False, datecompleted_manager_approval__isnull=True).order_by('-datecompleted')
    return render(request, 'tasks/task_manager_pending.html', {
        'tasks': tasks
    })





@login_required
@allowed_user(allowed_roles=['customer'])
def task_client_pending(request):
    # Mostrar todas las tareas entregadas por employee, independientemente del usuario
    tasks = Task.objects.filter(datecompleted__isnull=False, datecompleted_manager_approval__isnull=False, datecompleted_client_approval__isnull=True).order_by('-datecompleted')
    return render(request, 'tasks/task_client_pending.html', {
        'tasks': tasks
    })


    



@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

