from .models import Notificacion, PlantillaNotificacion
from django.template import Template, Context
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


# =========================
# RENDER TEMPLATE
# =========================
def render_template(texto, contexto):
    template = Template(texto)
    return template.render(Context(contexto))


# =========================
# CREAR NOTIFICACIÓN
# =========================
def crear_notificacion(usuario, plantilla_nombre, cita=None, contexto=None):

    if contexto is None:
        contexto = {}

    try:
        plantilla = PlantillaNotificacion.objects.get(
            nombre=plantilla_nombre, activo=True
        )
    except PlantillaNotificacion.DoesNotExist:
        print(f"❌ No existe plantilla: {plantilla_nombre}")
        return None

    asunto = render_template(plantilla.asunto_plantilla, contexto)
    cuerpo = render_template(plantilla.cuerpo_plantilla, contexto)

    notificacion = Notificacion.objects.create(
        usuario=usuario,
        plantilla=plantilla,
        cita=cita,
        canal=plantilla.canal,
        asunto=asunto,
        cuerpo_mensaje=cuerpo,
    )

    print("📩 Notificación creada")
    return notificacion

from django.core.mail import get_connection
import ssl

connection = get_connection()
connection.ssl_context = ssl._create_unverified_context()
# =========================
# ENVIAR EMAIL
# =========================
import requests
from django.conf import settings


def enviar_email(notificacion):

    try:

        payload = {
            "sender": {
                "name": "Little Pets",
                "email": "littlepetscolombia@gmail.com"
            },
            "to": [
                {
                    "email": notificacion.usuario.correo
                }
            ],
            "subject": notificacion.asunto,
            "htmlContent": f"""
            <html>
                <body>
                    {notificacion.cuerpo_mensaje}
                </body>
            </html>
            """
        }

        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json"
        }

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code in [200, 201, 202]:
            notificacion.marcar_enviada()
            print("✅ Email enviado por API Brevo")

        else:
            raise Exception(response.text)

    except Exception as e:

        print("❌ ERROR API:", e)
        notificacion.marcar_error(str(e))