from django.urls import path
from . import views
from .views import *



app_name = 'facturacion'

urlpatterns = [
   path('facturas/', lista_facturas, name='lista_facturas'),
   path('factura/<int:factura_id>/', detalle_factura, name='detalle_factura'),
   path('crear/<int:cita_id>/',crear_factura_servicio,name='crear_factura'),

   path('crear-servicio/<int:cita_id>/', crear_factura_servicio, name='crear_factura_servicio'),

   path('facturas/veterinario/', views.lista_facturas_vet, name='lista_facturas_vet'),
]