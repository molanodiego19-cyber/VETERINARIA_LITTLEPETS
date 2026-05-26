from datetime import datetime, timedelta, time
from .models import Cita

# 🔥 MAPEAR DÍAS (con tildes correctas)
dias_map = {
    "monday": "lunes",
    "tuesday": "martes",
    "wednesday": "miercoles",
    "thursday": "jueves",
    "friday": "viernes",
    "saturday": "sabado",
    "sunday": "domingo",
}


def veterinario_disponible(veterinario, fecha, hora, servicio):

    # 🔥 Convertir día a formato consistente
    dia_semana = dias_map[fecha.strftime("%A").lower()].lower()
    dias_vet = [d.lower() for d in veterinario.dias_laborales]

    # 🔴 Validar día laboral
    if dia_semana not in dias_vet:
        return False

    # 🔴 Validar horario del veterinario
    if not (veterinario.horario_inicio <= hora < veterinario.horario_fin):
        return False

    inicio = datetime.combine(fecha, hora)
    fin = inicio + timedelta(minutes=servicio.duracion_minutos)

    # 🔴 Validar cruce con otras citas
    citas = Cita.objects.filter(
        veterinario=veterinario,
        fecha=fecha,
        estado__in=['pendiente', 'confirmada']
    )

    for cita in citas:
        cita_inicio = datetime.combine(cita.fecha, cita.hora)
        cita_fin = cita_inicio + timedelta(
            minutes=cita.servicio.duracion_minutos
        )

        if inicio < cita_fin and fin > cita_inicio:
            return False

    return True


# ------------------------------------------------------------------------
def generar_horarios_disponibles(fecha, servicio, veterinarios):

    horarios_disponibles = []
    ahora = datetime.now()

    for vet in veterinarios:

        dia = dias_map[fecha.strftime("%A").lower()].lower()
        dias_vet = [d.lower() for d in vet.dias_laborales]

        if dia not in dias_vet:
            continue

        hora_actual = vet.horario_inicio

        while hora_actual < vet.horario_fin:

            inicio = datetime.combine(fecha, hora_actual)
            fin = inicio + timedelta(minutes=servicio.duracion_minutos)

            # 🔴 BLOQUE CLAVE: NO MOSTRAR HORAS PASADAS SI ES HOY
            if fecha == ahora.date() and inicio <= ahora:
                hora_actual = (
                    datetime.combine(fecha, hora_actual)
                    + timedelta(minutes=30)
                ).time()
                continue

            ocupado = False

            citas = Cita.objects.filter(
                veterinario=vet,
                fecha=fecha,
                estado__in=['pendiente', 'confirmada', 'en_proceso']
            )

            for cita in citas:

                c_inicio = datetime.combine(cita.fecha, cita.hora)
                c_fin = c_inicio + timedelta(minutes=cita.servicio.duracion_minutos)

                if inicio < c_fin and fin > c_inicio:
                    ocupado = True
                    break

            if not ocupado:

                horarios_disponibles.append({
                    "hora": hora_actual.strftime("%H:%M"),
                    "veterinario_id": vet.id
                })

            hora_actual = (
                datetime.combine(fecha, hora_actual)
                + timedelta(minutes=30)
            ).time()

    return horarios_disponibles