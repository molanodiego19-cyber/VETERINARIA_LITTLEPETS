from datetime import timedelta
from io import TextIOWrapper
import csv
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    TemplateView,
    UpdateView,
    ListView,
    CreateView,
    DeleteView,
    DetailView
)

from usuarios.models import (
    Usuario,
    Propietario,
    Veterinario
)

from mascota.models import (
    Mascota,
    Raza
)

from citas.models import (
    Cita,
    HistoriaClinica,
    Servicio
)

from .forms import (
    PropietarioUpdateForm,
    CambiarPasswordForm
)

from .forms_panel import *

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

def carga_masiva_propietarios(request):

    # VALIDAR SESION
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    try:

        usuario_admin = Usuario.objects.get(
            id=usuario_id
        )

    except Usuario.DoesNotExist:

        messages.error(
            request,
            'Usuario no encontrado'
        )

        return redirect('usuarios:login')

    # VALIDAR ROL
    if usuario_admin.rol != Usuario.Rol.ADMIN:

        messages.error(
            request,
            'No tienes permisos'
        )

        return redirect(
            'panel:panel_dashboard'
        )

    # POST
    if request.method == 'POST':

        archivo = request.FILES.get('archivo')

        # VALIDAR ARCHIVO
        if not archivo:

            messages.error(
                request,
                'Debes subir un archivo CSV'
            )

            return redirect(
                'usuarios:carga_masiva_propietarios'
            )

        # VALIDAR EXTENSION
        if not archivo.name.endswith('.csv'):

            messages.error(
                request,
                'Solo se permiten archivos CSV'
            )

            return redirect(
                'usuarios:carga_masiva_propietarios'
            )

        try:

            archivo_csv = TextIOWrapper(
                archivo.file,
                encoding='utf-8'
            )

            lector = csv.DictReader(
                archivo_csv
            )

            creados = 0
            errores = []

            for numero_fila, fila in enumerate(lector, start=2):

                try:

                    correo = fila.get(
                        'correo',
                        ''
                    ).strip()

                    # VALIDAR CORREO VACIO
                    if not correo:

                        errores.append(
                            f'Fila {numero_fila}: correo vacío'
                        )

                        continue

                    # VALIDAR DUPLICADO
                    if Usuario.objects.filter(
                        correo=correo
                    ).exists():

                        errores.append(
                            f'Fila {numero_fila}: el correo "{correo}" ya existe'
                        )

                        continue

                    # CREAR USUARIO
                    usuario = Usuario.objects.create(
                        correo=correo,
                        password=make_password(
                            fila.get('password', '')
                        ),
                        rol='propietario',
                        estado='activo'
                    )

                    # CREAR PROPIETARIO
                    Propietario.objects.create(
                        usuario=usuario,
                        nombre=fila.get('nombre', '').strip(),
                        apellido=fila.get('apellido', '').strip(),
                        telefono=fila.get('telefono', '').strip(),
                        tipo_documento=fila.get('tipo_documento', '').strip(),
                        documento=fila.get('documento', '').strip(),
                        ciudad=fila.get('ciudad', '').strip(),
                        direccion=fila.get('direccion', '').strip()
                    )

                    creados += 1

                except Exception as e:

                    errores.append(
                        f'Fila {numero_fila}: {str(e)}'
                    )

            # MENSAJE EXITOSO
            messages.success(
                request,
                f'Se crearon correctamente {creados} propietarios'
            )

            # MENSAJES DE ERROR
            if errores:

                messages.warning(
                    request,
                    f'Se encontraron {len(errores)} errores'
                )

                for error in errores:

                    messages.error(
                        request,
                        error
                    )

            return redirect(
                'usuarios:carga_masiva_propietarios'
            )

        except Exception as e:

            messages.error(
                request,
                f'Error general: {str(e)}'
            )

            return redirect(
                'usuarios:carga_masiva_propietarios'
            )

    return render(
        request,
        'panel/propietario/carga_masiva_propietario.html'
    )

from django.http import HttpResponse
import csv


def descargar_plantilla_propietarios(request):

    response = HttpResponse(
        content_type='text/csv'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="plantilla_propietarios.csv"'


    writer = csv.writer(response)

    # ENCABEZADOS
    writer.writerow([
        'correo',
        'password',
        'nombre',
        'apellido',
        'telefono',
        'tipo_documento',
        'documento',
        'ciudad',
        'direccion'
    ])

    # FILA DE EJEMPLO
    writer.writerow([
        'usuario@gmail.com',
        '123456',
        'Juan',
        'Perez',
        '3001234567',
        'CC',
        '123456789',
        'Bogota',
        'Calle 123'
    ])

    return response