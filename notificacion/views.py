from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from notificacion.services import enviar_email
from notificacion.models import Notificacion
from django.shortcuts import get_object_or_404


@csrf_exempt
def run_scheduler(request):

    print("🔥 ENTRÓ A RUN SCHEDULER")  # <- CLAVE

    try:
        from notificacion.tasks import (
            enviar_recordatorios,
            procesar_correos_pendientes,
            enviar_vacunas_pendientes
        )

        print("✔ imports OK")

        enviar_recordatorios()
        print("✔ recordatorios OK")

        procesar_correos_pendientes()
        print("✔ correos OK")

        enviar_vacunas_pendientes()
        print("✔ vacunas OK")

        return JsonResponse({"ok": True})

    except Exception as e:
        import traceback
        print("❌ ERROR EN SCHEDULER")
        print(traceback.format_exc())

        return JsonResponse({
            "ok": False,
            "error": str(e)
        }, status=500)