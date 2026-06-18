from django.urls import path

from . import views

app_name = "mascota"
urlpatterns = [
        path("registro-mascota/", views.registro_mascota_view, name="registro_mascota"),
    path("mascotas/", views.MascotaListView.as_view(), name="mascotas"),
    path("mascotas/nueva/", views.MascotaCreateView.as_view(), name="mascota_crear"),
    path(
        "mascotas/<int:pk>/editar/", views.MascotaUpdateView.as_view(), name="mascota_editar"
    ),
    path(
        "mascota/<int:pk>/eliminar/",
        views.eliminar_mascota,
        name="eliminar_mascota",
    ),
    path("mascotas/<int:pk>/", views.MascotaDetailView.as_view(), name="mascota_detalle"),
    # ---------RAZAS--------------- Y SERVICIOS
    path("ajax/cargar-razas/", views.cargar_razas, name="ajax_cargar_razas"),
]