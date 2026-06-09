from django.urls import path
from . import views
from .views import (
    CitaCreateView,
    CitasListView,
    AgendarCitaRecepcionistaView,
    CitaUpdateView,
    cancelar_cita,
    horarios_disponibles,
    iniciar_consulta,
    CitaRecepcionistaCreateView,
    cargar_razas
)


app_name = "citas"

urlpatterns = [
    path("", views.index, name="index"),
    # -------------CRUD CITAS-----------------------------------
    path("listar", CitasListView.as_view(), name="listar"),
    path("crear/", AgendarCitaRecepcionistaView.as_view(), name="crear"),
    path("crear/cita/", CitaCreateView.as_view(), name="crear_cita"),
    path("cancelar/<int:pk>/", cancelar_cita, name="cancelar"),
    path("reagendar/<int:pk>/", CitaUpdateView.as_view(), name="reagendar"),

    path("citas/ajax/cargar-razas/", cargar_razas, name="cargar_razas"),
    path(
        "historial-servicios/<int:mascota_id>/",
        views.historial_servicios_mascota,
        name="historial_servicios_mascota",
    ),
    path(
        "tratamiento/crear/<int:consulta_id>/",
        views.crear_tratamiento,
        name="crear_tratamiento",
    ),
    path("horarios/", horarios_disponibles, name="horarios"),
    path("iniciar-consulta/<int:cita_id>/", iniciar_consulta, name="iniciar_consulta"),
    path(
        "crear-consulta/<int:cita_id>/",
        views.CrearConsultaView.as_view(),
        name="crear_consulta",
    ),
    path(
        "crear-vacunacion/<int:cita_id>/",
        views.crear_vacunacion,
        name="crear_vacunacion",
    ),
    path(
        "historia-mascota/<int:mascota_id>/",
        views.historia_clinica_mascota,
        name="historia_mascota",
    ),
    path("consulta/", views.consulta, name="consulta"),
    path("historiaclinica/", views.historiaclinica, name="historiaclinica"),
    path("categoriaservicio/", views.categoriaservicio, name="categoriaservicio"),
    path("servicio/", views.servicio, name="servicio"),
    path("medicamento/", views.medicamento, name="medicamento"),
    path("tratamiento/", views.tratamiento, name="tratamiento"),
    # Eliminar
    path(
        "consulta/eliminar/<int:pk>/", views.eliminar_consulta, name="eliminar_consulta"
    ),
    path(
        "historiaclinica/eliminar/<int:pk>/",
        views.eliminar_historiaclinica,
        name="eliminar_historiaclinica",
    ),
    path(
        "categoriaservicio/eliminar/<int:pk>/",
        views.eliminar_categoriaservicio,
        name="eliminar_categoriaservicio",
    ),
    path(
        "servicio/eliminar/<int:pk>/", views.eliminar_servicio, name="eliminar_servicio"
    ),
    path(
        "tratamiento/eliminar/<int:pk>/",
        views.eliminar_tratamiento,
        name="eliminar_tratamiento",
    ),
    # Editar
    path("consulta/editar/<int:pk>/", views.editar_consulta, name="editar_consulta"),
    path(
        "historiaclinica/editar/<int:pk>/",
        views.editar_historiaclinica,
        name="editar_historiaclinica",
    ),
    path(
        "categoriaservicio/editar/<int:pk>/",
        views.editar_categoriaservicio,
        name="editar_categoriaservicio",
    ),
    path("servicio/editar/<int:pk>/", views.editar_servicio, name="editar_servicio"),
    path(
        "medicamento/editar/<int:pk>/",
        views.editar_medicamento,
        name="editar_medicamento",
    ),
    path(
        "tratamiento/editar/<int:pk>/",
        views.editar_tratamiento,
        name="editar_tratamiento",
    ),
    # -----------------------------
    # VACUNACION
    # ---------------------------------------
    path("vacunas/agendadas/", views.vacunas_agendadas, name="vacunas_agendadas"),
    path(
        "cita/<int:cita_id>/confirmar/",
        views.confirmar_cita_recepcionista,
        name="confirmar_cita_recepcionista",
    ),
    path(
        "recepcion/cita/agendar/",
        CitaRecepcionistaCreateView.as_view(),
        name="agendar_cita_recepcionista",
    ),
]
