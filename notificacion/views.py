from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.mail import send_mail

from notificacion.tasks import (
    enviar_recordatorios,
    procesar_correos_pendientes,
    enviar_vacunas_pendientes
)


# =========================
# RUN SCHEDULER CON CELERY
# =========================
def run_scheduler(request):

    try:
        enviar_recordatorios.delay()
        procesar_correos_pendientes.delay()
        enviar_vacunas_pendientes.delay()

        return JsonResponse({
            "ok": True,
            "msg": "Tareas enviadas a Celery"
        })

    except Exception as e:
        return JsonResponse({
            "ok": False,
            "error": str(e)
        }, status=500)


# =========================
# TEST EMAIL
# =========================
def test_email(request):

    try:

        send_mail(
            subject="Test Brevo",
            message="Email de prueba desde Django",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                settings.EMAIL_HOST_USER
            ],
            fail_silently=False,
        )

        return HttpResponse(
            "✅ Email enviado correctamente"
        )

    except Exception as e:

        return HttpResponse(
            f"❌ ERROR: {str(e)}"
        )


# =========================
# INFO SMTP
# =========================
def smtp_info(request):

    return HttpResponse(
        f"""
        HOST: {settings.EMAIL_HOST}<br>
        PORT: {settings.EMAIL_PORT}<br>
        TLS: {settings.EMAIL_USE_TLS}<br>
        USER: {settings.EMAIL_HOST_USER}<br>
        """
    )