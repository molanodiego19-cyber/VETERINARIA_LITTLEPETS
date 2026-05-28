from django.urls import path
from .views import run_scheduler

urlpatterns = [
    path('run-scheduler/', run_scheduler, name='run_scheduler'),
]