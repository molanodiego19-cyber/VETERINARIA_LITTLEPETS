import threading
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.mail import send_mail


# =========================
# RUN SCHEDULER (ASYNC)
# =========================
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
        "msg": "Scheduler ejecutado en background"
    })


# =========================
# TEST EMAIL (CORRECTO)
# =========================
def test_email(request):

    try:
        send_mail(
            subject="Test Brevo",
            message="Email de prueba desde Django",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["tu_correo@gmail.com"],
            fail_silently=False,
        )

        return HttpResponse("✅ Email enviado correctamente")

    except Exception as e:
        return HttpResponse(f"❌ ERROR: {str(e)}")


# =========================
# INFO SMTP
# =========================
def smtp_info(request):
    return HttpResponse(
        f"""
HOST: {settings.EMAIL_HOST}<br>
PORT: {settings.EMAIL_PORT}<br>
TLS: {settings.EMAIL_USE_TLS}<br>
USER: {settings.EMAIL_HOST_USER}
"""
    )