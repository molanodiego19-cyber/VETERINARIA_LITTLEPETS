from citas.models import Cita
from mascota.models import Mascota
from django.utils import timezone
from datetime import datetime

from notificacion.models import Notificacion
from notificacion.services import crear_notificacion, enviar_email


# =========================
# CORREOS PENDIENTES
# =========================
def procesar_correos_pendientes():

    pendientes = Notificacion.objects.filter(
        estado='pendiente',
        canal='email'
    )

    for n in pendientes:
        try:
            enviar_email(n)
        except Exception as e:
            print("❌ Error enviando email:", e)

    print("✅ Correos pendientes procesados")


# =========================
# RECORDATORIOS DE CITAS
# =========================
def enviar_recordatorios():

    ahora = timezone.now()
    citas = Cita.objects.filter(estado='pendiente')

    for cita in citas:

        cita_dt = timezone.make_aware(
            datetime.combine(cita.fecha, cita.hora)
        )

        horas = (cita_dt - ahora).total_seconds() / 3600

        enviar = False
        tipo = None

        if 0.4 <= horas <= 0.6:
            enviar = True
            tipo = "30m"

        elif 1.5 <= horas <= 2.5:
            enviar = True
            tipo = "2h"

        elif 23 <= horas <= 25:
            enviar = True
            tipo = "12h"

        if not enviar:
            continue

        usuario = cita.dueño.usuario

        contexto = {
            'nombre': cita.dueño.nombre,
            'mascota': cita.mascota.nombre,
            'fecha': cita.fecha,
            'hora': cita.hora,
            'servicio': cita.servicio.nombre,
            'tipo_recordatorio': tipo
        }

        crear_notificacion(
            usuario=usuario,
            plantilla_nombre='recordatorio_cita',
            cita=cita,
            contexto=contexto
        )

    print("✅ Recordatorios enviados")


# =========================
# VACUNAS
# =========================
def enviar_vacunas_pendientes():

    mascotas = Mascota.objects.all()

    for mascota in mascotas:

        usuario = mascota.propietario.usuario

        contexto = {
            'nombre': mascota.propietario.nombre,
            'mascota': mascota.nombre,
            'fecha': timezone.now().date(),
        }

        crear_notificacion(
            usuario=usuario,
            plantilla_nombre='vacuna_pendiente',
            contexto=contexto
        )

    print("✅ Vacunas enviadas")