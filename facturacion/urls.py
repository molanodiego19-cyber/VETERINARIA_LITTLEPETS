from django.urls import path
from .views import (
    lista_facturas,
    detalle_factura,
    crear_factura_servicio,
    facturas_pendientes,
    cobrar_factura
    )

app_name = "facturacion"

urlpatterns = [
    path("facturas/", lista_facturas, name="lista_facturas"),
    path("factura/<int:factura_id>/", detalle_factura, name="detalle_factura"),
    path("crear/<int:cita_id>/", crear_factura_servicio, name="crear_factura"),
    path(
        "crear-servicio/<int:cita_id>/",
        crear_factura_servicio,
        name="crear_factura_servicio",
    ),
    path("facturas/pendientes", facturas_pendientes, name="factura_pendiente"),
    path("marcar/pagada/<int:factura_id>/", cobrar_factura, name="marcar_pagada"),
]
