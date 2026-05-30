from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from notificacion.services import enviar_email
from notificacion.models import Notificacion
from django.shortcuts import get_object_or_404


import threading
from django.http import JsonResponse

def run_scheduler(request):

    def job():
        from notificacion.tasks import (
            enviar_recordatorios,
            procesar_correos_pendientes,
            enviar_vacunas_pendientes
        )

        enviar_recordatorios()
        procesar_correos_pendientes()
        enviar_vacunas_pendientes()

    threading.Thread(target=job).start()

    return JsonResponse({
        "ok": True,
        "msg": "Scheduler en background"
    })
from django.http import HttpResponse
from django.core.mail import send_mail

from django.http import HttpResponse
from django.core.mail import get_connection

from django.core.mail import send_mail
from django.http import HttpResponse

def test_email(request):

    try:
        send_mail(
            subject="Test Brevo",
            message="Email de prueba",
            from_email=None,
            recipient_list=["tu_correo@gmail.com"],
            fail_silently=False,
        )

        return HttpResponse("✅ Email enviado correctamente")

    except Exception as e:
        return HttpResponse(f"❌ ERROR: {str(e)}")

from django.http import HttpResponse
from django.conf import settings

def smtp_info(request):
    return HttpResponse(
        f"""
HOST: {settings.EMAIL_HOST}<br>
PORT: {settings.EMAIL_PORT}<br>
TLS: {settings.EMAIL_USE_TLS}<br>
USER: {settings.EMAIL_HOST_USER}
"""
    )