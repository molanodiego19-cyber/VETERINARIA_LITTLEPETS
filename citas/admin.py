from django.contrib import admin
from .models import *
from facturacion.models import *
from notificacion.models import *
from usuarios.models import *
from veterinarioapp.models import *
from mascota.models import *

# Registramos todos los modelos para que aparezcan en el admin
admin.site.register(CategoriaServicios)
admin.site.register(Cita)
admin.site.register(Consulta)
#admin.site.register(ConsultaServicio)
admin.site.register(HistoriaClinica)
admin.site.register(Medicamento)
admin.site.register(Servicio)
admin.site.register(Tratamiento)
#admin.site.register(TratamientoMedicamento)
admin.site.register(DetalleFactura)
admin.site.register(Factura)
admin.site.register(Especie)
admin.site.register(Mascota)
admin.site.register(Raza)
admin.site.register(Vacunacion)
admin.site.register(Vacuna)
admin.site.register(Notificacion)
admin.site.register(PlantillaNotificacion)
admin.site.register(Propietario)
admin.site.register(Usuario)
admin.site.register(Veterinario)
admin.site.register(Especialidad)
admin.site.register(HorarioVeterinario)
admin.site.register(BloqueoAgenda)
