# notificacion/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from django.template import Template, Context

from .models import (
    Notificacion,
    PlantillaNotificacion
)


# =====================================================
# RENDER TEMPLATE DINÁMICO
# =====================================================

def render_template(texto, contexto):

    template = Template(texto)

    return template.render(
        Context(contexto)
    )


# =====================================================
# CREAR NOTIFICACIÓN
# =====================================================

def crear_notificacion(
    usuario,
    plantilla_nombre,
    cita=None,
    contexto={}
):

    try:

        plantilla = PlantillaNotificacion.objects.get(
            nombre=plantilla_nombre,
            activo=True
        )

    except PlantillaNotificacion.DoesNotExist:

        print(f"❌ No existe plantilla: {plantilla_nombre}")
        return None

    # 🔥 renderizar variables dinámicas
    asunto = render_template(
        plantilla.asunto_plantilla,
        contexto
    )

    cuerpo = render_template(
        plantilla.cuerpo_plantilla,
        contexto
    )

    # 🔥 guardar notificación
    notificacion = Notificacion.objects.create(
        usuario=usuario,
        plantilla=plantilla,
        cita=cita,
        canal=plantilla.canal,
        asunto=asunto,
        cuerpo_mensaje=cuerpo
    )

    # SOLO guardar
    print("📩 Notificación pendiente")

    return notificacion


# =====================================================
# ENVIAR EMAIL
# =====================================================

def enviar_email(notificacion):

    try:

        # 🔥 HTML BONITO
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>

        <body style="
            margin:0;
            padding:0;
            background:#f4f6f9;
            font-family:Arial, sans-serif;
        ">

            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center" style="padding:40px 20px;">

                        <table width="600" cellpadding="0" cellspacing="0" style="
                            background:#ffffff;
                            border-radius:14px;
                            overflow:hidden;
                            box-shadow:0 4px 20px rgba(0,0,0,0.08);
                        ">

                            <!-- HEADER -->
                            <tr>
                                <td style="
                                    background:#2c3e50;
                                    padding:30px;
                                    text-align:center;
                                ">

                                    <h1 style="
                                        color:white;
                                        margin:0;
                                        font-size:28px;
                                    ">
                                        🐾 Little Pets
                                    </h1>

                                </td>
                            </tr>

                            <!-- CONTENIDO -->
                            <tr>
                                <td style="
                                    padding:40px;
                                    color:#333;
                                    line-height:1.7;
                                    font-size:15px;
                                ">

                                    {notificacion.cuerpo_mensaje}

                                </td>
                            </tr>

                            <!-- FOOTER -->
                            <tr>
                                <td style="
                                    background:#f8f8f8;
                                    padding:20px;
                                    text-align:center;
                                    font-size:12px;
                                    color:#777;
                                ">

                                    Este correo fue enviado automáticamente.<br>
                                    © Little Pets 2025

                                </td>
                  a         </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
        """

        email = EmailMultiAlternatives(
            subject=notificacion.asunto,
            body=notificacion.cuerpo_mensaje,
            from_email=settings.EMAIL_HOST_USER,
            to=[notificacion.usuario.correo]
        )

        email.attach_alternative(
            html_template,
            "text/html"
        )

        email.send()

        print("✅ Correo enviado")

        # 🔥 actualizar estado
        notificacion.marcar_enviada()

    except Exception as e:

        print("❌ ERROR EMAIL:", e)

        notificacion.marcar_error(e)


# =====================================================
# ENVIAR MANUALMENTE
# =====================================================

def enviar_notificacion_view(request, notificacion_id):

    notificacion = get_object_or_404(
        Notificacion,
        id=notificacion_id
    )

    enviar_email(notificacion)

    return JsonResponse({
        "ok": True,
        "mensaje": "Notificación enviada"
    })