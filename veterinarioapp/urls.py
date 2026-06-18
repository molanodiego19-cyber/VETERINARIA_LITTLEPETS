from django.urls import path
from . import views

urlpatterns = [
    path("crear-horario/", views.crear_horario, name="crear_horario"),
    path("crear-especialidad/", views.crear_especialidad, name="crear_especialidad"),
    path(
        "crear-bloqueo-agenda/", views.crear_bloqueo_agenda, name="crear_bloqueo_agenda"
    ),
]
