from django.urls import path
from . import views
from .views_panel import (
    PanelPropietarioView,
    HistorialListView,
    perfil_propietario,
    usuarios_suspendidos,
    reactivar_usuario,
    cargar_servicios,
)
from . import views_panel

app_name = "usuarios"

urlpatterns = [
    # -------------------------
    # AUTENTICACIÓN
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # -------------------------
    # REGISTRO
    # -------------------------
    path("registro/", views.registro_view, name="registro"),
    path("usuarios-suspendidos/", usuarios_suspendidos, name="usuarios_suspendidos"),
    path(
        "reactivar-usuario/<int:usuario_id>/",
        reactivar_usuario,
        name="reactivar_usuario",
    ),
    path("recuperar-password/", views.recuperar_password, name="recuperar_password"),
    path(
        "reset-password/<uidb64>/<token>/", views.reset_password, name="reset_password"
    ),
    # -------------------------
    # PANEL GENERAL (REDIRECCIONES)
    # -------------------------
    path("panel-admin/", views.panel_admin, name="panel_admin"),
    path(
        "panel-veterinario/",
        views_panel.PanelVeterinarioView.as_view(),
        name="panel_veterinario",
    ),
    path(
        "panel-recepcionista/",
        views_panel.PanelRecepcionistaView.as_view(),
        name="panel_recepcionista",
    ),
    path(
        "perfil-recepcionista/",
        views_panel.perfil_recepcionista,
        name="perfil_recepcionista",
    ),
    path(
        "contraseña-recepcionista/",
        views_panel.cambiar_password_recepcionista,
        name="contraseña_recepcionista",
    ),
    path("panel-propietario/", PanelPropietarioView.as_view(), name="dashboard"),
    # -------------------------
    # FUNCIONALIDADES PANEL
    # -------------------------
    path("perfil/", perfil_propietario, name="perfil"),
    path(
        "perfil_veterinario/", views_panel.perfil_veterinario, name="perfil_veterinario"
    ),

    path("citas-veterinario/", views_panel.citas_veterinario, name="citas_veterinario"),
    # ---------RAZAS--------------- Y SERVICIOS
    path("ajax/cargar-servicios/", cargar_servicios, name="ajax_cargar_servicios"),
    # ----------------------------------------------
    path("historial/", HistorialListView.as_view(), name="historial"),
    path("contraseña/", views_panel.cambiar_password, name="contraseña"),
    path(
        "contraseñavet/",
        views_panel.cambiar_password_veterinario,
        name="contraseña_vet",
    ),
    # ADMIN EXTRA
    path("usuarios/", views.listar_usuarios, name="usuarios_listar"),
]
