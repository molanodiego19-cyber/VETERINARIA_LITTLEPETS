from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from notificacion.tasks import (
    enviar_recordatorios,
    procesar_correos_pendientes,
    enviar_vacunas_pendientes
)
from django.conf import settings

print("EMAIL_HOST_USER SETTINGS:", settings.EMAIL_HOST_USER)
@csrf_exempt
def run_scheduler(request):

    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=400)

    try:
        print("🔥 ENTRÓ A RUN SCHEDULER")

        enviar_recordatorios()
        print("✔ recordatorios OK")

        procesar_correos_pendientes()
        print("✔ correos OK")

        enviar_vacunas_pendientes()
        print("✔ vacunas OK")

        return JsonResponse({
            "ok": True,
            "mensaje": "Scheduler ejecutado correctamente"
        })

    except Exception as e:
        print("❌ ERROR RUN SCHEDULER:", e)

        return JsonResponse({
            "ok": False,
            "error": str(e)
        }, status=500)