from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.mail import send_mail

from notificacion.tasks import (
    enviar_recordatorios,
    procesar_correos_pendientes,
    enviar_vacunas_pendientes,
)
from django.http import HttpResponse
from django.conf import settings

import socket
from django.http import HttpResponse

def smtp_test(request):
    try:
        sock = socket.create_connection(
            ("smtp-relay.brevo.com", 587),
            timeout=10
        )
        sock.close()
        return HttpResponse("✅ Conexion SMTP OK")
    except Exception as e:
        return HttpResponse(f"❌ ERROR SMTP: {e}")

def smtp_info(request):
    return HttpResponse(f"""
        HOST: {settings.EMAIL_HOST}<br>
        PORT: {settings.EMAIL_PORT}<br>
        USER: {settings.EMAIL_HOST_USER}<br>
        PASSWORD: {'CONFIGURADA' if settings.EMAIL_HOST_PASSWORD else 'VACIA'}<br>
    """)
# =========================
# RUN SCHEDULER CON CELERY
# =========================
def run_scheduler(request):

    try:
        enviar_recordatorios.delay()
        procesar_correos_pendientes.delay()
        enviar_vacunas_pendientes.delay()

        return JsonResponse({"ok": True, "msg": "Tareas enviadas a Celery"})

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


# =========================
# TEST EMAIL
# =========================
def test_email(request):
    from django.conf import settings

    return HttpResponse(f"""
        HOST={settings.EMAIL_HOST}<br>
        PORT={settings.EMAIL_PORT}<br>
        USER={settings.EMAIL_HOST_USER}<br>
        PASS={'SI' if settings.EMAIL_HOST_PASSWORD else 'NO'}<br>
    """)