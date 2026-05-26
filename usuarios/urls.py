from django.urls import path
from . import views
from .views_panel import *
from . import views_panel

app_name = 'usuarios'

urlpatterns = [

    # -------------------------
    # INDEX
    # -------------------------
    path('', views.index, name='index'),

    # -------------------------
    # AUTENTICACIÓN
    # -------------------------
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # -------------------------
    # REGISTRO
    # -------------------------
    path('registro/', views.registro_view, name='registro'),
    path('registro-mascota/', views.registro_mascota_view, name='registro_mascota'),


    path('usuarios-suspendidos/', usuarios_suspendidos, name='usuarios_suspendidos'),
    path('reactivar-usuario/<int:usuario_id>/', reactivar_usuario, name='reactivar_usuario'),

    path('recuperar-password/',views.recuperar_password,name='recuperar_password'),
    path('reset-password/<uidb64>/<token>/',views.reset_password,name='reset_password'),
    # -------------------------
    # PANEL GENERAL (REDIRECCIONES)
    # -------------------------
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-veterinario/', views_panel.PanelVeterinarioView.as_view(), name='panel_veterinario'),

    # 👇 ESTE ES EL IMPORTANTE
    path('panel-propietario/', PanelPropietarioView.as_view(), name='dashboard'),

    # -------------------------
    # FUNCIONALIDADES PANEL
    # -------------------------
    path('perfil/', perfil_propietario, name='perfil'),
    path('perfil_veterinario/', views_panel.perfil_veterinario, name='perfil_veterinario'),

    path('mascotas/', MascotaListView.as_view(), name='mascotas'),
    path('mascotas/nueva/', MascotaCreateView.as_view(), name='mascota_crear'),
    path('mascotas/<int:pk>/editar/', MascotaUpdateView.as_view(), name='mascota_editar'),
    path('mascota/<int:pk>/eliminar/', views_panel.eliminar_mascota, name='eliminar_mascota'),
    path('mascotas/<int:pk>/', MascotaDetailView.as_view(), name='mascota_detalle'),

    path('citas-veterinario/', views_panel.citas_veterinario, name='citas_veterinario'),
    #---------RAZAS--------------- Y SERVICIOS
    path('ajax/cargar-razas/', cargar_razas, name='ajax_cargar_razas'),

    path('ajax/cargar-servicios/', cargar_servicios, name='ajax_cargar_servicios'),
    #----------------------------------------------

    path('historial/', HistorialListView.as_view(), name='historial'),

    path('contraseña/', views_panel.cambiar_password, name='contraseña'),
    path('contraseñavet/', views_panel.cambiar_password_veterinario, name='contraseña_vet'),



    # -------------------------
    # ADMIN EXTRA
    # -------------------------
    path('usuarios/', views.listar_usuarios, name='usuarios_listar'),
]