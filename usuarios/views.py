from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Propietario
from citas.models import Cita
from django.views.decorators.cache import never_cache
from notificacion.tasks import crear_notificacion
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse


# 🔐 helper para validar sesión
def usuario_logueado(request):
    return request.session.get("usuario_id")


# ---------------- LOGIN ----------------
def login_view(request):

    if request.method == "POST":

        correo = request.POST.get("correo")
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(correo=correo)

        except Usuario.DoesNotExist:
            return render(
                request, "usuarios/login.html", {"error": "❌ Usuario no existe"}
            )
        
        if usuario.estado in [
            Usuario.Estado.SUSPENDIDO,
            Usuario.Estado.INACTIVO,
        ]:
            return render(
                request,
                "usuarios/login.html",
                {
                    "error":f" Usuario {usuario.estado}. contacta al administrador"
                },
            )


       

        # SI EL BLOQUEO YA TERMINÓ
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta <= timezone.now():
            usuario.bloqueado_hasta = None
            usuario.intentos_fallidos = 3
            usuario.save()

        # USUARIO BLOQUEADO
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > timezone.now():

            minutos = (
                int((usuario.bloqueado_hasta - timezone.now()).total_seconds() // 60)
                + 1
            )

            return render(
                request,
                "usuarios/login.html",
                {
                    "error": f"❌ Usuario bloqueado. Intenta nuevamente en {minutos} minutos."
                },
            )

        # PASSWORD CORRECTA
        if check_password(password, usuario.password):

            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
            usuario.last_login = timezone.now()
            usuario.save()

            request.session["usuario_id"] = usuario.id
            request.session["usuario_rol"] = usuario.rol

            if usuario.rol == Usuario.Rol.ADMIN:
                return redirect("panel:panel_dashboard")

            elif usuario.rol == Usuario.Rol.VETERINARIO:
                return redirect("usuarios:panel_veterinario")

            elif usuario.rol == Usuario.Rol.RECEPCIONISTA:
                return redirect("usuarios:panel_recepcionista")

            return redirect("usuarios:dashboard")

        # PASSWORD INCORRECTA
        usuario.intentos_fallidos += 1

        # SUSPENDER A LOS 6
        if usuario.intentos_fallidos >= 6:

            usuario.estado = Usuario.Estado.SUSPENDIDO
            usuario.bloqueado_hasta = None
            usuario.fecha_suspension = timezone.now()
            usuario.motivo_suspension = "Múltiples intentos fallidos"

            mensaje = "❌ Usuario suspendido por múltiples intentos fallidos."

        # BLOQUEO A LOS 3
        elif usuario.intentos_fallidos == 3:

            usuario.bloqueado_hasta = timezone.now() + timedelta(minutes=5)

            mensaje = (
                "❌ Usuario bloqueado por 5 minutos.\n"
                "⚠️ Después del bloqueo tendrás 3 intentos más antes de suspensión."
            )

        # PRIMEROS 2 INTENTOS
        elif usuario.intentos_fallidos < 3:

            restantes = 3 - usuario.intentos_fallidos

            mensaje = (
                f"❌ Credenciales incorrectas. "
                f"Te quedan {restantes} intentos antes del bloqueo."
            )

        # DESPUÉS DEL BLOQUEO
        else:

            restantes = 6 - usuario.intentos_fallidos

            mensaje = (
                f"❌ Credenciales incorrectas. "
                f"Te quedan {restantes} intentos antes de suspensión."
            )

        usuario.save()

        return render(request, "usuarios/login.html", {"error": mensaje})

    return render(request, "usuarios/login.html")
from notificacion.services import crear_notificacion
from notificacion.models import Notificacion

def recuperar_password(request):

    if request.method == "POST":

        correo = request.POST.get("correo")

        if not correo:
            messages.error(request, "Correo requerido")
            return render(request, "usuarios/recuperar_password.html")

        usuario = Usuario.objects.filter(correo=correo).first()

        if not usuario:
            messages.error(request, "No existe una cuenta con ese correo")
            return render(request, "usuarios/recuperar_password.html")

        token_generator = PasswordResetTokenGenerator()

        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        token = token_generator.make_token(usuario)

        link = request.build_absolute_uri(
            reverse("usuarios:reset_password", kwargs={"uidb64": uid, "token": token})
        )

        crear_notificacion(
            usuario=usuario,
            plantilla_nombre="recuperar_password",
            contexto={"link": link},
        )

        messages.success(request, "Se envió un enlace al correo.")

    return render(request, "usuarios/recuperar_password.html")

def reset_password(request, uidb64, token):

    token_generator = PasswordResetTokenGenerator()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    if usuario and token_generator.check_token(usuario, token):

        if request.method == "POST":

            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            if password1 != password2:

                messages.error(request, "Las contraseñas no coinciden.")

            else:

                usuario.password = make_password(password1)

                usuario.save()

                messages.success(request, "Contraseña actualizada.")

                return redirect("usuarios:login")

        return render(request, "usuarios/reset_password.html")

    return render(request, "usuarios/reset_invalido.html")


# ---------------- REGISTRO ----------------
def registro_view(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        try:
            validate_email(correo)
        except ValidationError:
            return render(
                request,
                "usuarios/registro.html",
                {"error": "Correo electrónico inválido"},
            )

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
            return render(
                request,
                "usuarios/registro.html",
                {"error": "Correo no válido (debe tener dominio como .com, .co, etc.)"},
            )

        password = request.POST.get("password")

        # 🔥 validar correo
        if Usuario.objects.filter(correo=correo).exists():
            return render(
                request,
                "usuarios/registro.html",
                {"error": "El correo ya está registrado"},
            )

        documento = request.POST.get("documento")
        # 🔥 validar documento
        if Propietario.objects.filter(documento=documento).exists():
            return render(
                request,
                "usuarios/registro.html",
                {"error": "El documento ya está registrado"},
            )

        telefono = request.POST.get("telefono")

        # VALIDACION DE TELEFONO YA EXISTENTE
        if Propietario.objects.filter(telefono=telefono).exists():
            return render(
                request,
                "usuarios/registro.html",
                {"error": "El teléfono ya está registrado"},
            )

        usuario = Usuario.objects.create(
            correo=correo, password=make_password(password), rol=Usuario.Rol.PROPIETARIO
        )

        propietario = Propietario.objects.create(
            nombre=request.POST.get("nombre").upper(),
            apellido=request.POST.get("apellido").upper(),
            telefono=request.POST.get("telefono"),
            tipo_documento=request.POST.get("tipo_documento"),
            documento=documento,
            ciudad=request.POST.get("ciudad"),
            direccion=request.POST.get("direccion"),
            usuario=usuario,
        )

        # =====================================================
        # 🔔 NOTIFICACIÓN DE CUENTA CREADA
        # =====================================================

        contexto = {
            "nombre": propietario.nombre,
            "correo": usuario.correo,
        }

        crear_notificacion(
            usuario=usuario, plantilla_nombre="cuenta_creada", contexto=contexto
        )

        # 🔥 guardar en sesión para siguiente paso
        request.session["registro_propietario_id"] = propietario.id

        return redirect("mascota:registro_mascota")

    return render(request, "usuarios/registro.html")


# ---------------- LOGOUT ----------------


def logout_view(request):
    request.session.flush()
    return redirect("citas:index")


# ---------------- PANEL ADMIN ----------------
def panel_admin(request):
    if not usuario_logueado(request):
        return redirect("usuarios:login")

    return render(request, "panel/dashboard.html")


# ---------------- PANEL VETERINARIO ----------------


def panel_veterinario(request):
    if not usuario_logueado(request):
        return redirect("usuarios:login")

    return render(request, "panel/dashboard_veterinario.html")


# ---------------- PANEL RECEPCIONISTA ----------------
def panel_recepcionista(request):
    if not usuario_logueado(request):
        return redirect("usuarios:login")

    return render(request, "panel/dashboard_recepcionista.html")


# ---------------- PANEL PROPIETARIO ----------------
@never_cache
def panel_propietario(request):
    if not usuario_logueado(request):
        return redirect("usuarios:login")

    usuario_id = request.session.get("usuario_id")
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if not hasattr(usuario, "propietario"):
        return redirect("usuarios:login")

    propietario = usuario.propietario

    mascotas = Mascota.objects.filter(propietario=propietario)
    citas = Cita.objects.filter(dueño=propietario)

    return render(
        request,
        "usuarios/dashboard.html",
        {
            "propietario": propietario,
            "mascotas": mascotas,
            "citas": citas,
        },
    )


# ---------------- DASHBOARD ----------------
def dashboard(request):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=usuario_id)
    propietario = usuario.propietario

    ahora = timezone.now()

    citas = Cita.objects.filter(
        dueño=propietario,
        estado="pendiente",
        fecha__gte=ahora.date(),  # 🔥 solo futuras
    ).order_by("fecha", "hora")[
        :5
    ]  # 🔥 las más próximas (limite opcional)

    mascotas = Mascota.objects.filter(propietario=propietario)

    return render(
        request,
        "usuarios/dashboard.html",
        {"propietario": propietario, "mascotas": mascotas, "citas": citas},
    )


# ---------------- LISTAR USUARIOS ----------------
def listar_usuarios(request):
    if not usuario_logueado(request):
        return redirect("usuarios:login")

    usuarios = Usuario.objects.all()

    return render(request, "panel/listar_usuarios.html", {"usuarios": usuarios})
