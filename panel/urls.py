from django.urls import path
from . import views

app_name = "panel"

urlpatterns = [
    path("", views.dashboard, name="panel_dashboard"),
    path("perfil_propietario/", views.perfil_propietario, name="perfil_propietario"),
    path("perfil_veterinario/", views.perfil_veterinario, name="perfil_veterinario"),
    # RECEPCIONISTA
    path("recepcionistas/",views.RecepcionistaListView.as_view(),name="panel_recepcionista_list",),
    path("recepcionistas/crear/", views.RecepcionistaCreateView.as_view(), name="panel_recepcionista_create",),
    path("recepcionistas/<int:pk>/editar/", views.RecepcionistaUpdateView.as_view(),name="panel_recepcionista_edit",),
    path("recepcionistas/<int:pk>/eliminar/",views.RecepcionistaDeleteView.as_view(),name="panel_recepcionista_delete",),
    path("recepcionistas/reporte/pdf/",views.reporte_recepcionistas_pdf,name="reporte_recepcionistas_pdf",),
    path("recepcionistas/reporte/excel/", views.reporte_recepcionistas_excel,name="reporte_recepcionistas_excel",),
    # MASCOTAS
    path("mascotas/", views.MascotaListView.as_view(), name="panel_mascota_list"),
    path("mascotas/nueva/",views.MascotaCreateView.as_view(),name="panel_mascota_create",),
    path("mascotas/<int:pk>/editar/",views.MascotaUpdateView.as_view(),name="panel_mascota_edit",),
    path("mascotas/<int:pk>/eliminar/",views.MascotaDeleteView.as_view(),name="panel_mascota_delete",),
    # CONSULTAS
    path("consultas/", views.ConsultaListView.as_view(), name="panel_consulta_list"),
    path(
        "consultas/nueva/",
        views.ConsultaCreateView.as_view(),
        name="panel_consulta_create",
    ),
    path(
        "consultas/<int:pk>/editar/",
        views.ConsultaUpdateView.as_view(),
        name="panel_consulta_edit",
    ),
    path(
        "consultas/<int:pk>/eliminar/",
        views.ConsultaDeleteView.as_view(),
        name="panel_consulta_delete",
    ),
    # HISTORIACLINICA
    path(
        "historiaclinica/",
        views.HistoriaListView.as_view(),
        name="panel_historiaclinica_list",
    ),
    path(
        "historiaclinica/nueva/",
        views.HistorialCreateView.as_view(),
        name="panel_historiaclinica_create",
    ),
    path(
        "historiaclinica/<int:pk>/editar/",
        views.HistorialUpdateView.as_view(),
        name="panel_historiaclinica_edit",
    ),
    path(
        "historiaclinica/<int:pk>/eliminar/",
        views.HistorialDeleteView.as_view(),
        name="panel_historiaclinica_delete",
    ),
    # CATEGORÍA SERVICIOS
    path(
        "categoriaservicio/",
        views.CategoriaServicioListView.as_view(),
        name="panel_categoriaservicio_list",
    ),
    path(
        "categoriaservicio/nueva/",
        views.CategoriaServicioCreateView.as_view(),
        name="panel_categoriaservicio_create",
    ),
    path(
        "categoriaservicio/<int:pk>/editar/",
        views.CategoriaServicioUpdateView.as_view(),
        name="panel_categoriaservicio_edit",
    ),
    path(
        "categoriaservicio/<int:pk>/eliminar/",
        views.CategoriaServicioDeleteView.as_view(),
        name="panel_categoriaservicio_delete",
    ),
    # SERVICIOS
    path("servicio/", views.ServicioListView.as_view(), name="panel_servicio_list"),
    path(
        "servicio/nuevo/",
        views.ServicioCreateView.as_view(),
        name="panel_servicio_create",
    ),
    path(
        "servicio/<int:pk>/editar/",
        views.ServicioUpdateView.as_view(),
        name="panel_servicio_edit",
    ),
    path(
        "servicio/<int:pk>/eliminar/",
        views.ServicioDeleteView.as_view(),
        name="panel_servicio_delete",
    ),
    # FACTURAS Y DETALLE FACTURA
    path("factura/<int:pk>/pdf/", views.factura_pdf_view, name="factura_pdf"),
    path("facturas/pdf/", views.factura_pdf_list, name="factura_pdf_list"),
    path(
        "detallefactura/pdf/",
        views.detalle_factura_pdf_list,
        name="detalle_factura_pdf_list",
    ),
    path(
        "detallefactura/",
        views.DetalleFacturaListView.as_view(),
        name="panel_detallefactura_list",
    ),
    path(
        "detallefactura/nuevo/",
        views.DetalleFacturaCreateView.as_view(),
        name="panel_detallefactura_create",
    ),
    path(
        "detallefactura/<int:pk>/editar/",
        views.DetalleFacturaUpdateView.as_view(),
        name="panel_detallefactura_edit",
    ),
    path(
        "detallefactura/<int:pk>/eliminar/",
        views.DetalleFacturaDeleteView.as_view(),
        name="panel_detallefactura_delete",
    ),
    path("especies/", views.EspecieListView.as_view(), name="panel_especie_list"),
    path(
        "especies/nueva/",
        views.EspecieCreateView.as_view(),
        name="panel_especie_create",
    ),
    path(
        "especies/<int:pk>/editar/",
        views.EspecieUpdateView.as_view(),
        name="panel_especie_edit",
    ),
    path(
        "especies/<int:pk>/eliminar/",
        views.EspecieDeleteView.as_view(),
        name="panel_especie_delete",
    ),
    # RAZAS
    path("razas/", views.RazaListView.as_view(), name="panel_raza_list"),
    path("razas/nueva/", views.RazaCreateView.as_view(), name="panel_raza_create"),
    path(
        "razas/<int:pk>/editar/", views.RazaUpdateView.as_view(), name="panel_raza_edit"
    ),
    path(
        "razas/<int:pk>/eliminar/",
        views.RazaDeleteView.as_view(),
        name="panel_raza_delete",
    ),
    # VACUNA
    path("vacunas/", views.VacunaListView.as_view(), name="panel_vacuna_list"),
    path(
        "vacunas/nueva/", views.VacunaCreateView.as_view(), name="panel_vacuna_create"
    ),
    path(
        "vacunas/<int:pk>/editar/",
        views.VacunaUpdateView.as_view(),
        name="panel_vacuna_edit",
    ),
    path(
        "vacunas/<int:pk>/eliminar/",
        views.VacunaDeleteView.as_view(),
        name="panel_vacuna_delete",
    ),
    # VACUNACION
    path(
        "vacunacion/", views.VacunacionListView.as_view(), name="panel_vacunacion_list"
    ),
    path(
        "vacunacion/<int:pk>/editar/",
        views.VacunacionUpdateView.as_view(),
        name="panel_vacunacion_edit",
    ),
    path(
        "vacunacion/<int:pk>/eliminar/",
        views.VacunacionDeleteView.as_view(),
        name="panel_vacunacion_delete",
    ),
    # PLANTILLAS NOTIFICACION
    path(
        "plantillas/",
        views.PlantillaNotificacionListView.as_view(),
        name="panel_plantilla_list",
    ),
    path(
        "plantillas/nueva/",
        views.PlantillaNotificacionCreateView.as_view(),
        name="panel_plantilla_create",
    ),
    path(
        "plantillas/<int:pk>/editar/",
        views.PlantillaNotificacionUpdateView.as_view(),
        name="panel_plantilla_edit",
    ),
    path(
        "plantillas/<int:pk>/eliminar/",
        views.PlantillaNotificacionDeleteView.as_view(),
        name="panel_plantilla_delete",
    ),
    # NOTIFICACIONES
    path(
        "notificaciones/",
        views.NotificacionListView.as_view(),
        name="panel_notificacion_list",
    ),
    path(
        "notificaciones/nueva/",
        views.NotificacionCreateView.as_view(),
        name="panel_notificacion_create",
    ),
    path(
        "notificaciones/<int:pk>/editar/",
        views.NotificacionUpdateView.as_view(),
        name="panel_notificacion_edit",
    ),
    path(
        "notificaciones/<int:pk>/eliminar/",
        views.NotificacionDeleteView.as_view(),
        name="panel_notificacion_delete",
    ),
    # ESPECIALIDADES
    path(
        "especialidades/",
        views.EspecialidadListView.as_view(),
        name="panel_especialidad_list",
    ),
    path(
        "especialidades/nueva/",
        views.EspecialidadCreateView.as_view(),
        name="panel_especialidad_create",
    ),
    path(
        "especialidades/<int:pk>/editar/",
        views.EspecialidadUpdateView.as_view(),
        name="panel_especialidad_edit",
    ),
    path(
        "especialidades/<int:pk>/eliminar/",
        views.EspecialidadDeleteView.as_view(),
        name="panel_especialidad_delete",
    ),
    # FACTURAS
    path("facturas/", views.FacturaListViewAdmin.as_view(), name="panel_factura_list"),
    path(
        "facturas/recepcionista/",
        views.FacturaListViewRecepcionista.as_view(),
        name="panel_factura_list_recepcionista",
    ),
    path(
        "facturas/nueva/",
        views.FacturaCreateView.as_view(),
        name="panel_factura_create",
    ),
    path(
        "facturas/<int:pk>/editar/",
        views.FacturaUpdateView.as_view(),
        name="panel_factura_edit",
    ),
    path(
        "facturas/<int:pk>/eliminar/",
        views.FacturaDeleteView.as_view(),
        name="panel_factura_delete",
    ),
    path("facturas/<int:pk>/pdf/", views.factura_pdf_view, name="factura_pdf_view"),
    # CITAS
    path("citas/", views.CitasListView.as_view(), name="panel_cita_list"),
    # =========================
    # PROPIETARIOS
    # =========================
    path(
        "propietarios/",
        views.PropietarioListView.as_view(),
        name="panel_propietario_list",
    ),
    path(
        "propietarios/nuevo/",
        views.PropietarioCreateView.as_view(),
        name="panel_propietario_create",
    ),
    path(
        "propietarios/<int:pk>/editar/",
        views.PropietarioUpdateView.as_view(),
        name="panel_propietario_edit",
    ),
    path(
        "propietarios/<int:pk>/eliminar/",
        views.PropietarioDeleteView.as_view(),
        name="panel_propietario_delete",
    ),
    # =========================
    # VETERINARIOS
    # =========================
    path(
        "veterinarios/",
        views.VeterinarioListView.as_view(),
        name="panel_veterinario_list",
    ),
    path(
        "veterinarios/nuevo/",
        views.VeterinarioCreateView.as_view(),
        name="panel_veterinario_create",
    ),
    path(
        "veterinarios/<int:pk>/editar/",
        views.VeterinarioUpdateView.as_view(),
        name="panel_veterinario_edit",
    ),
    path(
        "veterinarios/<int:pk>/eliminar/",
        views.VeterinarioDeleteView.as_view(),
        name="panel_veterinario_delete",
    ),
    path("ajax/cargar-servicios/", views.cargar_servicios, name="cargar_servicios"),
    # Reportes
    path("servicios/historial/", views.historial_servicio, name="historial_servicio"),
    path(
        "servicio/reporte/pdf/", views.servicio_reporte_pdf, name="servicio_reporte_pdf"
    ),
    path(
        "reporte/mascotas/pdf/", views.reporte_mascotas_pdf, name="reporte_mascotas_pdf"
    ),
    # REPORTES CITAS
    path("citas/reporte/pdf/", views.reporte_citas_pdf, name="reporte_citas_pdf"),
    path("citas/reporte/excel/", views.reporte_citas_excel, name="reporte_citas_excel"),
    # REPORTES PROPIETARIOS
    path(
        "propietarios/reporte/pdf/",
        views.reporte_propietarios_pdf,
        name="reporte_propietarios_pdf",
    ),
    path(
        "propietarios/reporte/excel/",
        views.reporte_propietarios_excel,
        name="reporte_propietarios_excel",
    ),
    # REPORTES VETERINARIOS
    path(
        "veterinarios/reporte/pdf/",
        views.reporte_veterinarios_pdf,
        name="reporte_veterinarios_pdf",
    ),
    path(
        "veterinarios/reporte/excel/",
        views.reporte_veterinarios_excel,
        name="reporte_veterinarios_excel",
    ),
]
