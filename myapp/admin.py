from django.contrib import admin
from .models import Task
from import_export.admin import ImportExportModelAdmin

class TaskAdmin(ImportExportModelAdmin):
    readonly_fields = ("created", )

# Register your models here.
admin.site.register(Task, TaskAdmin)

