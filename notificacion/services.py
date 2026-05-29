from .models import Notificacion, PlantillaNotificacion
from django.template import Template, Context
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def render_template(texto, contexto):
    template = Template(texto)
    return template.render(Context(contexto))


from django.conf import settings
import traceback

def enviar_email(notificacion):

    try:

        print("HOST:", settings.EMAIL_HOST)
        print("PORT:", settings.EMAIL_PORT)
        print("USER:", settings.EMAIL_HOST_USER)
        print("DESTINO:", notificacion.usuario.correo)

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

        print("📤 Intentando enviar correo...")
        email.send()

        notificacion.marcar_enviada()
        print("✅ Email enviado")

    except Exception as e:

        print("❌ ERROR EMAIL:", str(e))
        print(traceback.format_exc())

        notificacion.marcar_error(str(e))