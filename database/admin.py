from django.contrib import admin
from django.apps import apps

models = apps.all_models['database']
admin.site.register(models.values())
