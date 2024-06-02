from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings  # new
from django.urls import path, include  # new
from django.conf.urls.static import static  # new
from .views import global_views, worker_tasks_views, models_views

urlpatterns = [    
    path('', global_views.index, name="index"),
    path('about/', global_views.about, name="about"),
    path('signin/', global_views.signin, name="signin"),
    path('signup/', global_views.signup, name="signup"),
    path('logout/', global_views.signout, name="logout"),


    path('tasks/', worker_tasks_views.tasks, name="tasks"),
    path('tasks/task_search', worker_tasks_views.task_search, name="task_search"),
    path('tasks_completed/', global_views.tasks_completed, name="tasks_completed"),

    path('approval_pending_tasks/<int:task_id>/<str:action>', global_views.task_client_pending, name="task_client_pending"),
    path('tasks/<int:task_id>/delete', global_views.delete_task, name="delete_task"),
    path('tasks_history/', global_views.tasks_history, name="tasks_history"),
    path('tasks_client_pending/', global_views.tasks_client_pending, name="tasks_client_pending"),

    path('tarea/<int:task_id>', models_views.get_task, name="get_task"),

    path('register-wash/', worker_tasks_views.register_wash, name='register_wash'),
]  


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #new