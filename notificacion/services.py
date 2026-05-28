from .models import Notificacion, PlantillaNotificacion
from django.template import Template, Context
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def render_template(texto, contexto):
    template = Template(texto)
    return template.render(Context(contexto))


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

    print("📩 Notificación pendiente")
    return notificacion


def enviar_email(notificacion):

    html_template = f"""
    <html>
    <body>
        {notificacion.cuerpo_mensaje}
    </body>
    </html>
    """

    email = EmailMultiAlternatives(
        subject=notificacion.asunto,
        body=notificacion.cuerpo_mensaje,
        from_email=settings.EMAIL_HOST_USER,
        to=[notificacion.usuario.correo]
    )

    email.attach_alternative(html_template, "text/html")

    try:
        email.send()
        notificacion.marcar_enviada()
        print("✅ Email enviado")

    except Exception as e:
        print("❌ ERROR EMAIL:", e)
        notificacion.marcar_error(str(e))