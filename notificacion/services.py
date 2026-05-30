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
            nombre=plantilla_nombre,
            activo=True
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
        cuerpo_mensaje=cuerpo
    )

    print("📩 Notificación creada")
    return notificacion


# =========================
# ENVIAR EMAIL
# =========================
def enviar_email(notificacion):

    try:
        print("HOST:", settings.EMAIL_HOST)
        print("USER:", settings.EMAIL_HOST_USER)
        print("DESTINO:", notificacion.usuario.correo)

        email = EmailMultiAlternatives(
            subject=notificacion.asunto,
            body=notificacion.cuerpo_mensaje,
            from_email=settings.EMAIL_HOST_USER,
            to=[notificacion.usuario.correo]
        )

        email.attach_alternative(
            f"<html><body>{notificacion.cuerpo_mensaje}</body></html>",
            "text/html"
        )

        email.send()

        notificacion.marcar_enviada()
        print("✅ Email enviado")

    except Exception as e:
        print("❌ ERROR EMAIL:", str(e))
        notificacion.marcar_error(str(e))