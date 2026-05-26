from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .models import Propietario, Veterinario
from mascota.models import Mascota, Raza
from citas.models import Cita, HistoriaClinica,Servicio
from .forms_panel import *
from django.db.models import Q
from django.views.generic import DetailView
from .forms_panel import CambiarPasswordForm
from django.http import JsonResponse
from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from .models import Propietario, Usuario
from mascota.models import Mascota
from citas.models import Cita, HistoriaClinica
from .forms_panel import *
from django.views.generic import DetailView
from .forms_panel import CambiarPasswordForm
from django.shortcuts import render, redirect
from .forms import PropietarioUpdateForm
from django.utils import timezone
from datetime import timedelta


from datetime import timedelta
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from .forms import CambiarPasswordForm


from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .forms import CambiarPasswordForm


from django.utils import timezone
from datetime import timedelta

def cambiar_password(request):

    propietario = obtener_propietario(request)

    if not propietario:
        return redirect('usuarios:login')

    usuario = propietario.usuario

    puede_cambiar = True
    dias_restantes = 0

    if usuario.fecha_cambio_password:

        diferencia = timezone.now() - usuario.fecha_cambio_password

        if diferencia < timedelta(days=30):

            puede_cambiar = False
            dias_restantes =   - diferencia.days

    if request.method == 'POST':

        if not puede_cambiar:

            messages.error(
                request,
                f"Debes esperar {dias_restantes} días para volver a cambiar la contraseña."
            )

            return redirect('usuarios:cambiar_password')

        form = CambiarPasswordForm(usuario, request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Contraseña actualizada correctamente"
            )

            return redirect('usuarios:perfil')

    else:

        form = CambiarPasswordForm(usuario)

    return render(request, 'usuarios/cambiar_password.html', {

        'form': form,
        'puede_cambiar': puede_cambiar,
        'dias_restantes': dias_restantes

    })

def cambiar_password_veterinario(request):
    veterinario = obtener_veterinario(request)

    if not veterinario:
        return redirect('usuarios:login')

    usuario = veterinario.usuario
    dias_restantes = 0

    if usuario.fecha_cambio_password:
        diferencia = timezone.now() - usuario.fecha_cambio_password

        if diferencia < timedelta(days=30):
            dias_restantes = 30 - diferencia.days

    if request.method == 'POST':

        if dias_restantes > 0:
            messages.error(
                request,
                f"❌ Debes esperar {dias_restantes} días para volver a cambiar la contraseña."
            )
            return redirect('usuarios:cambiar_password_veterinario')

        form = CambiarPasswordForm(usuario, request.POST)

        if form.is_valid():

            usuario.password = make_password(
                form.cleaned_data['nueva_password']
            )

            usuario.fecha_cambio_password = timezone.now()
            usuario.save()

            messages.success(
                request,
                "✅ Contraseña actualizada correctamente"
            )

            return redirect('usuarios:perfil_veterinario')

        messages.error(
            request,
            "❌ Error al cambiar la contraseña"
        )

    else:
        form = CambiarPasswordForm(usuario)

    return render(request, 'usuarios/cambiar_password_vet.html', {
        'form': form,
        'dias_restantes': dias_restantes
    })
#---------------------------------------------------------------------------


# 🔐 función reutilizable
def obtener_propietario(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return None

    return Propietario.objects.filter(usuario__id=usuario_id).first()

def obtener_veterinario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return None

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        return getattr(usuario, 'veterinario', None)
    except Usuario.DoesNotExist:
        return None
    
# ---------------- DASHBOARD ----------------
class PanelPropietarioView(TemplateView):
    template_name = 'usuarios/panel/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('usuarios:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        propietario = obtener_propietario(self.request)
        context['propietario'] = propietario
        context['mascotas'] = Mascota.objects.filter(propietario=propietario)
        context['citas'] = Cita.objects.filter(mascota__propietario=propietario).order_by('fecha', 'hora')
        return context

class PanelVeterinarioView(TemplateView):
    template_name = 'usuarios/dashboard_veterinario.html'

    def dispatch(self, request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('usuarios:login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        veterinario = obtener_veterinario(self.request)
        context['veterinario'] = veterinario

        hoy = timezone.now().date()

        if veterinario:

            # 🔹 Citas del día
            citas = Cita.objects.filter(
                veterinario=veterinario,
                fecha=hoy,
            ).order_by('fecha', 'hora')

            context['citas'] = citas

            # 🔹 Contador de citas confirmadas del día
            context['citas_confirmadas_count'] = Cita.objects.filter(
                veterinario=veterinario,
                fecha=hoy,
                estado='confirmada'
            ).count()

            # 🔹 Mascotas con citas con este veterinario
            context['mascotas'] = Mascota.objects.filter(
                citas__veterinario=veterinario
            ).distinct()

        else:
            context['citas'] = []
            context['mascotas'] = []
            context['citas_confirmadas_count'] = 0

        return context
    
# ---------------- PERFIL ----------------
def perfil_propietario(request):
    propietario = obtener_propietario(request)

    if not propietario:
        return redirect('usuarios:login')


    editar = request.GET.get('editar')

    if request.method == 'POST':
        form = PropietarioUpdateForm(request.POST, request.FILES, instance=propietario)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente")
            return redirect('usuarios:perfil')
    else:
        form = PropietarioUpdateForm(instance=propietario)

    return render(request, 'usuarios/perfil_editar.html', {
        'propietario': propietario,
        'form': form,
        'editar': editar
    })

def perfil_veterinario(request):
    veterinario = obtener_veterinario(request)

    if not veterinario:
        messages.error(request, "❌ No tienes un perfil de veterinario.")
        return redirect('usuarios:login')

    editar = request.GET.get('editar')

    if request.method == 'POST':
        form = PerfilVeterinarioForm(request.POST, request.FILES, instance=veterinario)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente")
            return redirect('usuarios:perfil_veterinario')
    else:
        form = PerfilVeterinarioForm(instance=veterinario)

    return render(request, 'usuarios/perfil_veterinario.html', {
        'veterinario': veterinario,
        'form': form,
        'editar': editar
    })
    
# ---------------- MASCOTAS ----------------
class MascotaListView(ListView):
    model = Mascota
    template_name = 'usuarios/mascotas_list.html'

    def get_queryset(self):
        propietario = obtener_propietario(self.request)

        if not propietario:
            return Mascota.objects.none()

        return Mascota.objects.filter(propietario=propietario,estado='activo')
    

#-------------OBTENER RAZAS------------------

def cargar_razas(request):
    especie_id = request.GET.get('especie_id')
    razas = Raza.objects.filter(tipo_especie_id=especie_id).values('id', 'nombre')
    return JsonResponse(list(razas), safe=False)
#-------------OBTENER SERVICIOS------------------
def cargar_servicios(request):
    especialidad_id = request.GET.get('especialidad_id')
    servicios = Servicio.objects.filter(especialidad_id=especialidad_id).values('id', 'nombre')
    return JsonResponse(list(servicios), safe=False)

#------------------------------------------------------------    
    
class MascotaCreateView(CreateView):
    model = Mascota
    form_class = MascotaForm
    template_name = 'usuarios/mascota_form.html'
    success_url = reverse_lazy('usuarios:mascotas')

    def form_valid(self, form):
        propietario = obtener_propietario(self.request)
        form.instance.propietario = propietario
        return super().form_valid(form)


class MascotaUpdateView(UpdateView):
    model = Mascota
    fields = ['nombre', 'raza','foto', 'fecha_nacimiento','peso_kg','esterilizacion']
    template_name = 'usuarios/mascota_form.html'
    success_url = reverse_lazy('usuarios:mascotas')

    def get_queryset(self):
        propietario = obtener_propietario(self.request)
        return Mascota.objects.filter(propietario=propietario)


def eliminar_mascota(request, pk):
    propietario = obtener_propietario(request)

    mascota = get_object_or_404(
        Mascota,
        pk=pk,
        propietario=propietario
    )

    mascota.estado = "Inactivo"
    mascota.save()

    return redirect('usuarios:mascotas')



class MascotaDetailView(DetailView):
    model = Mascota
    template_name = 'usuarios/mascota_detalle.html'

    def get_queryset(self):
        propietario = obtener_propietario(self.request)
        return Mascota.objects.filter(propietario=propietario)

# ---------------- HISTORIAL ----------------
class HistorialListView(ListView):
    template_name = 'usuarios/historial.html'

    def get_queryset(self):
        propietario = obtener_propietario(self.request)
        return HistoriaClinica.objects.filter(mascota__propietario=propietario)
    
#---------------------------------

def citas_veterinario(request):
    veterinario = obtener_veterinario(request)

    if not veterinario:
        return redirect('usuarios:login')

    citas = Cita.objects.filter(veterinario=veterinario)

    # 🔹 filtros opcionales
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')

    if fecha:
        citas = citas.filter(fecha=fecha)

    if hora:
        citas = citas.filter(hora=hora)

    # 🔹 ordenar todas las citas (pasadas y futuras)
    citas = citas.order_by('fecha', 'hora')

    return render(request, 'usuarios/citas_veterinario.html', {
        'citas': citas,
        'veterinario': veterinario
    })

def usuarios_suspendidos(request):

    usuarios = Usuario.objects.filter(
        estado=Usuario.Estado.SUSPENDIDO
    ).select_related(
        'propietario',
        'veterinario'
    ).order_by('-fecha_suspension')

    # FILTROS
    buscar = request.GET.get('buscar')
    rol = request.GET.get('rol')
    fecha_suspension = request.GET.get('fecha_suspension')

    # BUSCADOR GENERAL
    if buscar:

        usuarios_propietarios = usuarios.filter(
            propietario__nombre__icontains=buscar
        ) | usuarios.filter(
            propietario__apellido__icontains=buscar
        ) | usuarios.filter(
            propietario__documento__icontains=buscar
        ) | usuarios.filter(
            correo__icontains=buscar
        )

        usuarios_veterinarios = usuarios.filter(
            veterinario__nombre__icontains=buscar
        ) | usuarios.filter(
            veterinario__apellido__icontains=buscar
        ) | usuarios.filter(
            veterinario__documento__icontains=buscar
        ) | usuarios.filter(
            correo__icontains=buscar
        )

        usuarios = (
            usuarios_propietarios |
            usuarios_veterinarios
        ).distinct()

    # FILTRO ROL
    if rol:
        usuarios = usuarios.filter(rol=rol)

    # FILTRO FECHA SUSPENSION
    if fecha_suspension:
        usuarios = usuarios.filter(
            fecha_suspension__date=fecha_suspension
        )

    return render(request, 'usuarios/usuarios_suspendidos.html', {
        'usuarios': usuarios
    })

def reactivar_usuario(request, usuario_id):

    usuario = get_object_or_404(Usuario, id=usuario_id)

    usuario.estado = Usuario.Estado.ACTIVO
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    usuario.fecha_suspension = None
    usuario.motivo_suspension = None

    usuario.save()

    messages.success(request, 'Usuario reactivado correctamente')

    return redirect('usuarios:usuarios_suspendidos')