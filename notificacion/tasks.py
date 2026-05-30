from celery import shared_task
from citas.models import Cita
from mascota.models import Mascota
from django.utils import timezone
from datetime import datetime

from notificacion.models import Notificacion
from notificacion.services import (
    crear_notificacion,
    enviar_email
)


@shared_task
def procesar_correos_pendientes():

    pendientes = Notificacion.objects.filter(
        estado='pendiente',
        canal='email'
    )

    print(f"📨 Correos pendientes: {pendientes.count()}")

    for n in pendientes:

        try:
            enviar_email(n)

        except Exception as e:
            print(
                f"❌ Error enviando correo ID {n.id}: {e}"
            )

    print("✅ Correos pendientes procesados")


@shared_task
def enviar_recordatorios():

    ahora = timezone.now()

    citas = Cita.objects.filter(
        estado='pendiente'
    )

    print(f"📅 Citas encontradas: {citas.count()}")

    for cita in citas:

        try:

            cita_dt = timezone.make_aware(
                datetime.combine(
                    cita.fecha,
                    cita.hora
                )
            )

            horas = (
                cita_dt - ahora
            ).total_seconds() / 3600

            tipo = None

            if 0.4 <= horas <= 0.6:
                tipo = "30m"

            elif 1.5 <= horas <= 2.5:
                tipo = "2h"

            elif 23 <= horas <= 25:
                tipo = "12h"

            if not tipo:
                continue

            crear_notificacion(
                usuario=cita.dueño.usuario,
                plantilla_nombre='recordatorio_cita',
                cita=cita,
                contexto={
                    'nombre': cita.dueño.nombre,
                    'mascota': cita.mascota.nombre,
                    'fecha': cita.fecha,
                    'hora': cita.hora,
                    'servicio': cita.servicio.nombre,
                    'tipo_recordatorio': tipo
                }
            )

            print(
                f"✅ Recordatorio creado para cita {cita.id}"
            )

        except Exception as e:

            print(
                f"❌ Error cita {cita.id}: {e}"
            )

    print("✅ Recordatorios procesados")


@shared_task
def enviar_vacunas_pendientes():

    mascotas = Mascota.objects.all()

    print(
        f"💉 Mascotas encontradas: {mascotas.count()}"
    )

    for mascota in mascotas:

        try:

            crear_notificacion(
                usuario=mascota.propietario.usuario,
                plantilla_nombre='vacuna_pendiente',
                contexto={
                    'nombre': mascota.propietario.nombre,
                    'mascota': mascota.nombre,
                    'fecha': timezone.now().date(),
                }
            )

            print(
                f"✅ Vacuna pendiente creada para {mascota.nombre}"
            )

        except Exception as e:

            print(
                f"❌ Error mascota {mascota.id}: {e}"
            )

    print("✅ Vacunas pendientes procesadas")