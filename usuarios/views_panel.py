from django.views.generic import TemplateView, UpdateView, ListView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .models import Propietario, Usuario
from mascota.models import Mascota, Raza
from citas.models import Cita, HistoriaClinica, Servicio
from .forms_panel import (
    PerfilVeterinarioForm,
    CambiarPasswordForm,
)
from .forms import PerfilRecepcionistaForm
from django.views.generic import DetailView
from django.http import JsonResponse
from .forms import PropietarioUpdateForm
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.db.models import Q


def calcular_bloqueo_password(usuario):

    if not usuario.fecha_cambio_password:

        return 0

    limite = usuario.fecha_cambio_password + timedelta(days=30)
    ahora = timezone.now()

    if ahora >= limite:
        return 0

    dias = (limite - ahora).days

    return dias + 1 if (limite - ahora).seconds > 0 else dias


def cambiar_password(request):

    propietario = obtener_propietario(request)

    if not propietario:
        return redirect("usuarios:login")

    usuario = propietario.usuario

    dias_restantes = calcular_bloqueo_password(usuario)
    puede_cambiar = dias_restantes == 0

    if request.method == "POST":

        if not puede_cambiar:
            messages.error(request, f"Debes esperar {dias_restantes} días")
            return redirect("usuarios:cambiar_password")

        form = CambiarPasswordForm(usuario, request.POST)

        if form.is_valid():
            form.save()
            usuario.fecha_cambio_password = timezone.now()
            usuario.save()

            messages.success(request, "Contraseña actualizada correctamente")
            return redirect("usuarios:perfil")

    else:
        form = CambiarPasswordForm(usuario)

    return render(
        request,
        "usuarios/cambiar_password.html",
        {
            "form": form,
            "dias_restantes": dias_restantes,
            "puede_cambiar": puede_cambiar,
        },
    )


def cambiar_password_recepcionista(request):

    recepcionista = obtener_recepcionista(request)

    if not recepcionista:
        return redirect("usuarios:login")

    usuario = recepcionista.usuario

    dias_restantes = calcular_bloqueo_password(usuario)
    puede_cambiar = dias_restantes == 0

    if request.method == "POST":

        if not puede_cambiar:
            messages.error(request, f"❌ Debes esperar {dias_restantes} días")
            return redirect("usuarios:contraseña_recepcionista")

        form = CambiarPasswordForm(usuario, request.POST)

        if form.is_valid():
            form.save()  # 👈 usa SOLO el form
            usuario.fecha_cambio_password = timezone.now()
            usuario.save()

            messages.success(request, "✅ Contraseña actualizada correctamente")
            return redirect("usuarios:perfil_recepcionista")

    else:
        form = CambiarPasswordForm(usuario)

    return render(
        request,
        "usuarios/cambiar_password_recepcionista.html",
        {
            "form": form,
            "dias_restantes": dias_restantes,
            "puede_cambiar": puede_cambiar,
        },
    )


def cambiar_password_veterinario(request):

    veterinario = obtener_veterinario(request)

    if not veterinario:
        return redirect("usuarios:login")

    usuario = veterinario.usuario

    dias_restantes = calcular_bloqueo_password(usuario)

    if request.method == "POST":

        if dias_restantes > 0:
            messages.error(request, f"❌ Debes esperar {dias_restantes} días")
            return redirect("usuarios:cambiar_password_veterinario")

        form = CambiarPasswordForm(usuario, request.POST)

        if form.is_valid():

            usuario.password = make_password(form.cleaned_data["password_nueva"])
            usuario.fecha_cambio_password = timezone.now()
            usuario.save()

            messages.success(request, "✅ Contraseña actualizada correctamente")
            return redirect("usuarios:perfil_veterinario")

    else:
        form = CambiarPasswordForm(usuario)

    return render(
        request,
        "usuarios/cambiar_password_vet.html",
        {"form": form, "dias_restantes": dias_restantes},
    )


# ---------------------------------------------------------------------------


# 🔐 función reutilizable
def obtener_propietario(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return None

    return Propietario.objects.filter(usuario__id=usuario_id).first()


def obtener_recepcionista(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return None

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return getattr(usuario, "recepcionista", None)
    except Usuario.DoesNotExist:
        return None


def obtener_veterinario(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return getattr(usuario, "veterinario", None)
    except Usuario.DoesNotExist:
        return None


# ---------------- DASHBOARD ----------------
class PanelPropietarioView(TemplateView):
    template_name = "usuarios/panel/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if "usuario_id" not in request.session:
            return redirect("usuarios:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        propietario = obtener_propietario(self.request)
        context["propietario"] = propietario
        context["mascotas"] = Mascota.objects.filter(propietario=propietario)
        context["citas"] = Cita.objects.filter(
            mascota__propietario=propietario
        ).order_by("fecha", "hora")
        return context


class PanelRecepcionistaView(TemplateView):
    template_name = "usuarios/dashboard_recepcionista.html"

    def dispatch(self, request, *args, **kwargs):
        if "usuario_id" not in request.session:
            return redirect("usuarios:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recepcionista = obtener_recepcionista(self.request)

        context["recepcionista"] = recepcionista

        hoy = timezone.now().date()

        if recepcionista:

            context["citas_hoy"] = Cita.objects.filter(fecha=hoy)

            context["proximas_citas"] = Cita.objects.filter(fecha__gt=hoy).order_by(
                "fecha", "hora"
            )[:5]

            context["propietarios"] = Propietario.objects.all()[:5]

            context["mascotas_recientes"] = Mascota.objects.order_by("-id")[:5]

        else:
            context["citas_hoy"] = []
            context["proximas_citas"] = []
            context["propietarios"] = []
            context["mascotas_recientes"] = []

        return context


class PanelVeterinarioView(TemplateView):
    template_name = "usuarios/dashboard_veterinario.html"

    def dispatch(self, request, *args, **kwargs):
        if "usuario_id" not in request.session:
            return redirect("usuarios:login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        veterinario = obtener_veterinario(self.request)
        context["veterinario"] = veterinario

        hoy = timezone.now().date()

        if veterinario:

            # 🔹 Citas del día
            citas = Cita.objects.filter(
                veterinario=veterinario,
                fecha=hoy,
            ).order_by("fecha", "hora")

            context["citas"] = citas

            # 🔹 Contador de citas confirmadas del día
            context["citas_confirmadas_count"] = Cita.objects.filter(
                veterinario=veterinario, fecha=hoy, estado="confirmada"
            ).count()

            # 🔹 Mascotas con citas con este veterinario
            context["mascotas"] = Mascota.objects.filter(
                citas__veterinario=veterinario
            ).distinct()

        else:
            context["citas"] = []
            context["mascotas"] = []
            context["citas_confirmadas_count"] = 0

        return context


# ---------------- PERFIL ----------------
def perfil_propietario(request):
    propietario = obtener_propietario(request)

    if not propietario:
        return redirect("usuarios:login")

    editar = request.GET.get("editar")

    if request.method == "POST":
        form = PropietarioUpdateForm(request.POST, request.FILES, instance=propietario)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente")
            return redirect("usuarios:perfil")
    else:
        form = PropietarioUpdateForm(instance=propietario)

    return render(
        request,
        "usuarios/perfil_editar.html",
        {"propietario": propietario, "form": form, "editar": editar},
    )


def perfil_recepcionista(request):

    recepcionista = obtener_recepcionista(request)

    if not recepcionista:
        return redirect("usuarios:login")

    if request.method == "POST":
        form = PerfilRecepcionistaForm(
            request.POST, request.FILES, instance=recepcionista
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect("usuarios:perfil_recepcionista")

    else:
        form = PerfilRecepcionistaForm(instance=recepcionista)

    return render(
        request,
        "usuarios/perfil_recepcionista.html",
        {
            "recepcionista": recepcionista,
            "form": form,
            "editar": request.GET.get("editar"),
        },
    )


def perfil_veterinario(request):
    veterinario = obtener_veterinario(request)

    if not veterinario:
        messages.error(request, "❌ No tienes un perfil de veterinario.")
        return redirect("usuarios:login")

    editar = request.GET.get("editar")

    if request.method == "POST":
        form = PerfilVeterinarioForm(request.POST, request.FILES, instance=veterinario)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente")
            return redirect("usuarios:perfil_veterinario")
    else:
        form = PerfilVeterinarioForm(instance=veterinario)

    return render(
        request,
        "usuarios/perfil_veterinario.html",
        {"veterinario": veterinario, "form": form, "editar": editar},
    )



# -------------OBTENER SERVICIOS------------------
def cargar_servicios(request):
    especialidad_id = request.GET.get("especialidad_id")
    servicios = Servicio.objects.filter(especialidad_id=especialidad_id).values(
        "id", "nombre"
    )
    return JsonResponse(list(servicios), safe=False)




# ---------------- HISTORIAL ----------------
class HistorialListView(ListView):
    template_name = "usuarios/historial.html"

    def get_queryset(self):
        propietario = obtener_propietario(self.request)
        return HistoriaClinica.objects.filter(mascota__propietario=propietario)


# ---------------------------------


from django.shortcuts import render, redirect

def citas_veterinario(request):
    veterinario = obtener_veterinario(request)

    if not veterinario:
        return redirect("usuarios:login")

    citas = Cita.objects.filter(
        veterinario=veterinario
    )

    # Filtros
    fecha = request.GET.get("fecha")
    hora = request.GET.get("hora")
    estado = request.GET.get("estado")
    mascota = request.GET.get("mascota")
    propietario = request.GET.get("propietario")

    if fecha:
        citas = citas.filter(fecha=fecha)

    if hora:
        citas = citas.filter(hora=hora)

    if estado:
        citas = citas.filter(estado=estado)

    if mascota:
        citas = citas.filter(
            mascota__nombre__icontains=mascota
        )

    if propietario:
        citas = citas.filter(
            mascota__propietario__nombre__icontains=propietario
        )

    citas = citas.order_by("fecha", "hora")

    return render(
        request,
        "usuarios/citas_veterinario.html",
        {
            "citas": citas,
            "veterinario": veterinario,
        },
    )


def usuarios_suspendidos(request):

    usuarios = (
        Usuario.objects.filter(
            estado__in=[
                Usuario.Estado.SUSPENDIDO,
                Usuario.Estado.INACTIVO,
            ]
        )
        .select_related("propietario", "veterinario")
        .order_by("-fecha_suspension")
    )

    # FILTROS
    buscar = request.GET.get("buscar")
    rol = request.GET.get("rol")
    fecha_suspension = request.GET.get("fecha_suspension")

    if buscar:

        usuarios_propietarios = (
            usuarios.filter(propietario__nombre__icontains=buscar)
            | usuarios.filter(propietario__apellido__icontains=buscar)
            | usuarios.filter(propietario__documento__icontains=buscar)
            | usuarios.filter(correo__icontains=buscar)
        )

        usuarios_veterinarios = (
            usuarios.filter(veterinario__nombre__icontains=buscar)
            | usuarios.filter(veterinario__apellido__icontains=buscar)
            | usuarios.filter(veterinario__documento__icontains=buscar)
            | usuarios.filter(correo__icontains=buscar)
        )

        usuarios = (usuarios_propietarios | usuarios_veterinarios).distinct()

    if rol:
        usuarios = usuarios.filter(rol=rol)

    if fecha_suspension:
        usuarios = usuarios.filter(
            fecha_suspension__date=fecha_suspension
        )

    suspendidos = usuarios.filter(
        estado=Usuario.Estado.SUSPENDIDO
    )

    inactivos = usuarios.filter(
        estado=Usuario.Estado.INACTIVO
    )

    return render(
        request,
        "usuarios/usuarios_suspendidos.html",
        {
            "suspendidos": suspendidos,
            "inactivos": inactivos,
        }
    )


def reactivar_usuario(request, usuario_id):

    usuario = get_object_or_404(Usuario, id=usuario_id)

    usuario.estado = Usuario.Estado.ACTIVO
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.fecha_suspension = None
    usuario.motivo_suspension = None

    usuario.save()

    messages.success(request, "Usuario reactivado correctamente")

    return redirect("usuarios:usuarios_suspendidos")


def citas_recepcionista(request):

    recepcionista = obtener_recepcionista(request)

    if not recepcionista:
        return redirect("usuarios:login")

    citas = Cita.objects.all().order_by("fecha", "hora")

    return render(
        request,
        "usuarios/citas_recepcionista.html",
        {"citas": citas, "recepcionista": recepcionista},
    )


def cambiar_estado_cita(request, cita_id):
    recepcionista = obtener_recepcionista(request)

    if not recepcionista:
        return redirect("usuarios:login")

    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")

        if nuevo_estado in ["pendiente", "en_espera", "atendido", "cancelado"]:

            cita.estado = nuevo_estado
            cita.save()

            messages.success(request, "Estado de la cita actualizado correctamente")

        return redirect("citas:recepcionista")

    return render(request, "usuarios/cambiar_estado_cita.html", {"cita": cita})
