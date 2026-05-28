import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veterinaria.settings')
django.setup()

from notificacion.scheduler import iniciar_scheduler

iniciar_scheduler()

print("🔥 Scheduler activo")

while True:
    time.sleep(60)

@csrf_exempt
def run_scheduler(request):

    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=400)

    # IMPORT LOCAL (evita circular import)
    from notificacion.tasks import (
        enviar_recordatorios,
        procesar_correos_pendientes,
        enviar_vacunas_pendientes
    )

    enviar_recordatorios()
    procesar_correos_pendientes()
    enviar_vacunas_pendientes()

    return JsonResponse({
        "ok": True,
        "mensaje": "Scheduler ejecutado"
    })