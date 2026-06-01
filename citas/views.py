from datetime import datetime, timedelta, date
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView
from mascota.models import Mascota
from notificacion.services import crear_notificacion
from usuarios.models import Usuario, Veterinario
from .forms import *
from .models import *
from .utils import generar_horarios_disponibles, veterinario_disponible


def index(request):
    return render(request, 'index.html')

def crear_objeto(request, form_class, template):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = form_class()
    return render(request, template, {'form': form})

#---------------------------------------------------------------
# VACUNAS AGENDADAS
#------------------------------------------------------------
def vacunas_agendadas(request):


    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')
    
    citas_vacunas = Cita.objects.filter(
        servicio__nombre__icontains='Vacuna'
    ).select_related(
        'mascota',
        'servicio',
        'vacuna'
    ).order_by('fecha', 'hora')

    context = {
        'citas_vacunas': citas_vacunas
    }

    return render(
        request,
        'citas/vacunas_agendadas.html', context

    )










#----------------------------------------------------------------------------------------------------------------------------------

def consulta(request):
    return crear_objeto(request, ConsultaForm, 'panel/form.html')

def historiaclinica(request):
    return crear_objeto(request, HistoriaClinicaForm, 'panel/form.html')

def categoriaservicio(request):
    return crear_objeto(request, CategoriaServiciosForm, 'panel/form.html')

def servicio(request):
    return crear_objeto(request, ServicioForm, 'panel/form.html')

def medicamento(request):
    return crear_objeto(request, MedicamentoForm, 'panel/form.html')

def tratamiento(request):
    return crear_objeto(request, TratamientoForm, 'panel/form.html')

def eliminar_consulta(request, pk):
    obj = get_object_or_404(Consulta, pk=pk)
    if request.method == 'POST':
        obj.delete()
    return redirect('dashboard')

def eliminar_historiaclinica(request, pk):
    obj = get_object_or_404(HistoriaClinica, pk=pk)
    if request.method == 'POST':
        obj.delete()
    return redirect('dashboard')

def eliminar_categoriaservicio(request, pk):
    obj = get_object_or_404(CategoriaServicios, pk=pk)
    if request.method == 'POST':
        obj.delete()
    return redirect('dashboard')

def eliminar_servicio(request, pk):
    obj = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        obj.delete()
    return redirect('dashboard')

def eliminar_medicamento(request, pk):
    obj = get_object_or_404(Medicamento, pk=pk)
    if request.method == 'POST':
        obj.delete()
    return redirect('dashboard')

def eliminar_tratamiento(request, pk):
    obj = get_object_or_404(Tratamiento, pk=pk)
    if request.method == 'POST':
        obj.delete()
    return redirect('dashboard')

def editar_consulta(request, pk):
    obj = get_object_or_404(Consulta, pk=pk)
    if request.method == 'POST':
        form = ConsultaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ConsultaForm(instance=obj)
    return render(request, 'panel/form.html', {'form': form})

def editar_historiaclinica(request, pk):
    obj = get_object_or_404(HistoriaClinica, pk=pk)
    if request.method == 'POST':
        form = HistoriaClinicaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = HistoriaClinicaForm(instance=obj)
    return render(request, 'panel/form.html', {'form': form})

def editar_categoriaservicio(request, pk):
    obj = get_object_or_404(CategoriaServicios, pk=pk)
    if request.method == 'POST':
        form = CategoriaServiciosForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CategoriaServiciosForm(instance=obj)
    return render(request, 'panel/form.html', {'form': form})

def editar_servicio(request, pk):
    obj = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ServicioForm(instance=obj)
    return render(request, 'panel/form.html', {'form': form})



def editar_medicamento(request, pk):
    obj = get_object_or_404(Medicamento, pk=pk)
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = MedicamentoForm(instance=obj)
    return render(request, 'panel/form.html', {'form': form})

def editar_tratamiento(request, pk):
    obj = get_object_or_404(Tratamiento, pk=pk)
    if request.method == 'POST':
        form = TratamientoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TratamientoForm(instance=obj)
    return render(request, 'panel/form.html', {'form': form})

#------------------CREAR CITA------------------
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Cita
from .forms import CitaForm
from usuarios.models import Usuario, Propietario

#filtros y reportes
# PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# EXCEL
import openpyxl


# =========================================================
# FUNCIÓN REUTILIZABLE PARA FILTRAR CITAS
# =========================================================

def filtrar_citas(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return Cita.objects.none()

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Cita.objects.none()

    # 🔐 SOLO PROPIETARIOS VEN SUS CITAS
    if hasattr(usuario, 'propietario'):
        citas = Cita.objects.filter(dueño=usuario.propietario)

    # 🔐 VETERINARIO VE SUS CITAS
    elif hasattr(usuario, 'veterinario'):
        citas = Cita.objects.filter(veterinario=usuario.veterinario)

    else:
        return Cita.objects.none().order_by('fecha', 'hora')

    # =========================
    # FILTROS
    # =========================

    estado = request.GET.get('estado')
    fecha = request.GET.get('fecha')
    servicio = request.GET.get('servicio')
    veterinario = request.GET.get('veterinario')

    if estado:
        citas = citas.filter(estado=estado)

    if fecha:
        citas = citas.filter(fecha=fecha)

    if servicio:
        citas = citas.filter(servicio_id=servicio)

    if veterinario:
        citas = citas.filter(veterinario_id=veterinario)

    return citas.order_by('-fecha', '-hora')


class CitaCreateView(CreateView):
    model = Cita
    form_class = CitaForm
    template_name = 'citas/cita_form.html'
    success_url = reverse_lazy('citas:listar')

    def get_template_names(self):

        rol = self.request.session.get('usuario_rol')

        if rol == Usuario.Rol.RECEPCIONISTA:
            return [
                'citas/cita_form_recepcionista.html'
            ]

        return [
            'citas/cita_form.html'
        ]

    def form_valid(self, form):
        # -------------------------------
        # 🔐 Obtener usuario desde sesión
        # -------------------------------
        usuario_id = self.request.session.get('usuario_id')

        if not usuario_id:
            form.add_error(None, "❌ Debes iniciar sesión")
            return self.form_invalid(form)

        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            form.add_error(None, "❌ Usuario no existe")
            return self.form_invalid(form)

        # -------------------------------
        # 👤 Validar que sea propietario
        # -------------------------------
        if not hasattr(usuario, 'propietario'):
            form.add_error(None, "❌ Este usuario no es propietario")
            return self.form_invalid(form)

        propietario = usuario.propietario

        # -------------------------------
        # 📅 Lógica de asignación
        # -------------------------------
        fecha = form.cleaned_data['fecha']
        hora = form.cleaned_data['hora']
        servicio = form.cleaned_data['servicio']


        # =====================================================
        # ⏰ VALIDAR ANTICIPACIÓN DE 2 HORAS
        # =====================================================

        # Combinar fecha y hora de la cita
        fecha_hora_cita = datetime.combine(fecha, hora)

        # Convertir a timezone local
        fecha_hora_cita = timezone.make_aware(
            fecha_hora_cita,
            timezone.get_current_timezone()
        )

        # Hora actual + 2 horas
        limite = timezone.now() + timedelta(hours=1)

        # Validar
        if fecha_hora_cita < limite:
            form.add_error(
                None,
                "❌ Las citas deben agendarse con mínimo 1 horas de anticipación"
            )
            return self.form_invalid(form)

        veterinarios = Veterinario.objects.filter(
            disponible=True,
            servicios=servicio
        )

        if servicio.especialista_required:
            veterinarios = veterinarios.filter(
                especialidad=servicio.especialista_required
            )

        veterinario_asignado = None

        for vet in veterinarios:
            if veterinario_disponible(vet, fecha, hora, servicio):
                veterinario_asignado = vet
                break

        if not veterinario_asignado:
            form.add_error(None, "❌ No hay veterinarios disponibles")
            return self.form_invalid(form)

        # -------------------------------
        # 💾 Guardar datos
        # -------------------------------
        form.instance.veterinario = veterinario_asignado
        form.instance.dueño = propietario

        # 🔥 guardar cita
        response = super().form_valid(form)

        # =====================================================
        # 🔔 CREAR NOTIFICACIÓN
        # =====================================================

        cita = self.object

        contexto = {
            'nombre': cita.dueño.nombre,
            'mascota': cita.mascota.nombre,
            'fecha': cita.fecha,
            'hora': cita.hora,
            'servicio': cita.servicio.nombre,
            'veterinario': cita.veterinario.nombre,
        }

        crear_notificacion(
            usuario=usuario,
            plantilla_nombre='cita_agendada',
            cita=cita,
            contexto=contexto
        )

        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    #------------------FECHA DESDE EL VIEW----
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today().isoformat()  # 🔥 clave
        return context


#------------LISTAR CITAS---------------------------
class CitasListView(ListView):

    model = Cita

    template_name = 'citas/cita_list.html'

    context_object_name = 'citas'

    # 🔐 PROTECCIÓN
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')
        return super().dispatch(request, *args, **kwargs)


    # ==========================================
    # QUERYSET FILTRADO
    # ==========================================

    def get_queryset(self):

        citas_filtradas = filtrar_citas(self.request)

        return citas_filtradas.exclude(servicio__nombre__icontains='Vacuna')

    # ==========================================
    # CONTEXTO
    # ==========================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['servicios'] = Servicio.objects.all()

        context['veterinarios'] = Veterinario.objects.all()

        context['estados'] = Cita.ESTADOS

        return context


# =========================================================
# REPORTE PDF
# =========================================================

def reporte_citas_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="reporte_citas.pdf"'

    doc = SimpleDocTemplate(response)

    elementos = []

    styles = getSampleStyleSheet()

    # ==========================================
    # TÍTULO
    # ==========================================

    titulo = Paragraph(
        "Reporte General de Citas",
        styles['Title']
    )

    elementos.append(titulo)

    elementos.append(Spacer(1, 20))

    # ==========================================
    # DATOS
    # ==========================================

    data = [[
        'ID',
        'Mascota',
        'Veterinario',
        'Servicio',
        'Fecha',
        'Hora',
        'Estado'
    ]]

    citas = filtrar_citas(request).exclude(servicio__nombre__icontains='Vacuna')

    for c in citas:

        data.append([
            str(c.id),
            str(c.mascota.nombre),
            str(c.veterinario) if c.veterinario else 'Sin asignar',
            str(c.servicio.nombre),
            str(c.fecha),
            str(c.hora),
            str(c.get_estado_display())
        ])

    # ==========================================
    # TABLA
    # ==========================================

    tabla = Table(data)

    tabla.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

    ]))

    elementos.append(tabla)

    # ==========================================
    # CONSTRUIR PDF
    # ==========================================

    doc.build(elementos)

    return response


# =========================================================
# REPORTE EXCEL
# =========================================================

def reporte_citas_excel(request):

    response = HttpResponse(
        content_type='application/ms-excel'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="reporte_citas.xlsx"'

    workbook = openpyxl.Workbook()

    worksheet = workbook.active

    worksheet.title = 'Citas'

    # ==========================================
    # ENCABEZADOS
    # ==========================================

    encabezados = [
        'ID',
        'Mascota',
        'Veterinario',
        'Servicio',
        'Fecha',
        'Hora',
        'Estado'
    ]

    worksheet.append(encabezados)

    # ==========================================
    # DATOS
    # ==========================================

    citas = filtrar_citas(request)

    for c in citas:

        worksheet.append([
            c.id,
            str(c.mascota.nombre),
            str(c.veterinario) if c.veterinario else 'Sin asignar',
            str(c.servicio.nombre),
            str(c.fecha),
            str(c.hora),
            str(c.get_estado_display())
        ])

    workbook.save(response)

    return response



#-------------CANCELAR CITAS-------------------------------------
def cancelar_cita(request, pk):

    cita = get_object_or_404(Cita, pk=pk)

    # 🔥 evitar cancelar dos veces
    if cita.estado == 'cancelada':
        messages.warning(request, "La cita ya estaba cancelada")
        return redirect('citas:listar')

    # 🔥 cambiar estado
    cita.estado = 'cancelada'
    cita.save()

    # =====================================================
    # 🔔 NOTIFICACIÓN
    # =====================================================

    usuario = cita.dueño.usuario

    contexto = {
        'nombre': cita.dueño.nombre,
        'mascota': cita.mascota.nombre,
        'fecha': cita.fecha,
        'hora': cita.hora,
        'servicio': cita.servicio.nombre,
        'veterinario': cita.veterinario.nombre,
    }

    crear_notificacion(
        usuario=usuario,
        plantilla_nombre='cita_cancelada',
        cita=cita,
        contexto=contexto
    )

    messages.success(request, "✅ Cita cancelada correctamente")

    return redirect('citas:listar')  

#------------------REAGENDAR---------------------------------
class CitaUpdateView(UpdateView):

    model = Cita

    form_class = ReagendarCitaForm

    template_name = 'citas/reagendar_cita.html'

    success_url = reverse_lazy('citas:listar')

    def form_valid(self, form):

        messages.success(
            self.request,
            "✅ La cita fue reagendada correctamente"
        )

        return super().form_valid(form)

#--------------HORARIO DISPONIBLE----------------------------
def horarios_disponibles(request):

    fecha_str = request.GET.get('fecha')
    servicio_id = request.GET.get('servicio')

    if not fecha_str or not servicio_id:
        return JsonResponse([], safe=False)

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    servicio = Servicio.objects.get(id=servicio_id)

    veterinarios = Veterinario.objects.filter(
        disponible=True,
        servicios=servicio
    )

    # filtro por especialidad
    if servicio.especialista_required:
        veterinarios = veterinarios.filter(
            especialidad=servicio.especialista_required
        )

    horarios = generar_horarios_disponibles(fecha, servicio, veterinarios)

    return JsonResponse(horarios, safe=False)

#-------------------------CALENDARIO--------------
def eventos_calendario(request):

    servicio_id = request.GET.get('servicio')

    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id=usuario_id)

    if hasattr(usuario, 'propietario'):
        citas = Cita.objects.filter(
            dueño=usuario.propietario,
            estado__in=['pendiente', 'confirmada']
    )
    elif hasattr(usuario, 'veterinario'):
        citas = Cita.objects.filter(
            veterinario=usuario.veterinario,
            estado__in=['pendiente', 'confirmada']
    )
    else:
        citas = Cita.objects.none()

    eventos = []

    for cita in citas:
        inicio = datetime.combine(cita.fecha, cita.hora)
        fin = inicio + timedelta(minutes=cita.servicio.duracion_minutos)

        eventos.append({
            "title": f"Ocupado",
            "start": inicio.isoformat(),
            "end": fin.isoformat(),
            "color": "red"
        })

    return JsonResponse(eventos, safe=False)


#-----proteccion

def dispatch(self, request, *args, **kwargs):

    if not request.session.get('usuario_id'):
        return redirect('usuarios:login')

    return super().dispatch(request, *args, **kwargs)

#-----iniciar consultas 

def iniciar_consulta(request, cita_id):

    cita = get_object_or_404(Cita, id=cita_id)

    if cita.estado in ['cancelada', 'finalizada']:
        messages.warning(request, "Esta cita no puede iniciarse")
        return redirect('usuarios:citas_veterinario')

    cita.estado = 'en_proceso'
    cita.save()

    categoria = cita.servicio.categoria.nombre_categoria.lower().strip()

    categorias_estetica = [
        'estética', 'estetica', 'baño', 'peluquería', 'peluqueria', 'spa'
    ]

    categorias_vacunacion = [
        'vacuna', 'vacunación', 'vacunacion', 'inmunización'
    ]

    # 🟡 ESTÉTICA
    if any(c in categoria for c in categorias_estetica):
        return redirect('citas:crear_historial_servicio', cita_id=cita.id)

    # 💉 VACUNACIÓN
    if any(c in categoria for c in categorias_vacunacion):
        return redirect('citas:crear_vacunacion', cita_id=cita.id)

    # 🩺 CONSULTA
    return redirect('citas:crear_consulta', cita_id=cita.id)

class CrearConsultaView(CreateView):
    model = Consulta
    form_class = ConsultaCompletaForm
    template_name = 'citas/crear_consulta.html'

    def get_initial(self):
        cita = get_object_or_404(Cita, id=self.kwargs.get('cita_id'))
        return {
            'fecha_inicio': cita.fecha,
            'fecha_fin': cita.fecha,
            'peso_en_consulta': cita.mascota.peso_kg if cita.mascota.peso_kg else None,
            'observaciones': cita.notas_adicionales,
            'mascota': cita.mascota,
            'veterinario': cita.veterinario,
        }
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = None
        accion = request.POST.get("accion")
        cita = get_object_or_404(Cita, id=self.kwargs.get('cita_id'))

        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        # ✅ GUARDAR CONSULTA SIEMPRE
        consulta = form.save(commit=False)
        consulta.cita = cita
        consulta.veterinario = cita.veterinario
        consulta.save()

        form.instance = consulta
        form.save_m2m()

        consulta.crear_historia_clinica()

        cita.estado = 'finalizada'
        cita.save()

        # 🔵 CASO 1: SOLO CONSULTA
        if accion != "tratamiento":
            messages.success(self.request, "✅ Consulta guardada correctamente.")
            return redirect('facturacion:crear_factura',cita_id=cita.id)

        # 🟡 CASO 2: CONSULTA + TRATAMIENTO
        return redirect('citas:crear_tratamiento', consulta_id=consulta.id)

    @transaction.atomic
    def form_valid(self, form):
        cita = get_object_or_404(Cita, id=self.kwargs.get('cita_id'))

        consulta = form.save(commit=False)
        consulta.cita = cita
        consulta.veterinario = cita.veterinario
        consulta.save()

        form.instance = consulta
        form.save_m2m()
        self.object = consulta

        # 🔥 CREAR HISTORIA CLÍNICA
        consulta.crear_historia_clinica()

        # 🔄 CAMBIAR ESTADO
        cita.estado = 'finalizada'
        cita.save()

        messages.success(self.request, "✅ Consulta guardada correctamente.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "❌ Error al guardar la consulta.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('facturacion:crear_factura', kwargs={'consulta_id': self.object.id})
    

def historia_clinica_mascota(request, mascota_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    mascota = get_object_or_404(Mascota, id=mascota_id)

    base_template = 'usuarios/base_panel.html'

    if hasattr(usuario, 'propietario'):

        if mascota.propietario != usuario.propietario:
            return redirect('usuarios:dashboard')

    elif hasattr(usuario, 'veterinario'):

        base_template = 'usuarios/base_veterinario.html'

    else:
        return redirect('usuarios:login')

    # ================= CONSULTAS =================

    consultas = HistoriaClinica.objects.filter(
        mascota=mascota,
        tipo_registro='consulta'
    ).select_related(
        'veterinario',
        'cita'
    ).order_by('-fecha_consulta')

    # ================= VACUNACIONES =================

    vacunaciones = Vacunacion.objects.filter(
        cita__mascota=mascota
    ).select_related(
        'vacuna',
        'cita',
        'cita__veterinario'
    ).order_by('-fecha_aplicacion')

    return render(request, 'citas/historia_mascota.html', {

        'mascota': mascota,
        'consultas': consultas,
        'vacunaciones': vacunaciones,
        'base_template': base_template

    })

def crear_tratamiento(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)

    # 🔐 validar sesión
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        messages.error(request, "Sesión no válida")
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if not hasattr(usuario, 'veterinario'):
        messages.error(request, "No autorizado")
        return redirect('login')

    veterinario = usuario.veterinario

    if request.method == 'POST':
        form = TratamientoForm(request.POST)

        if form.is_valid():
            tratamiento = form.save(commit=False)

            # 🔥 asignaciones automáticas
            tratamiento.consulta = consulta
            tratamiento.veterinario = veterinario
            tratamiento.fecha_creacion = timezone.now()

            tratamiento.save()

            messages.success(request, "💊 Tratamiento creado correctamente")
            return redirect('facturacion:crear_factura', cita_id=consulta.cita.id)

    else:
        form = TratamientoForm()

    return render(request, 'citas/crear_tratamiento.html', {
        'form': form,
        'consulta': consulta
    })

@transaction.atomic
def crear_historial_servicio(request, cita_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == 'POST':

        form = HistorialServiciosForm(request.POST)

        if form.is_valid():

            historial = form.save(commit=False)

            historial.cita = cita

            historial.save()

            cita.estado = 'finalizada'
            cita.save()

            messages.success(
                request,
                "Servicio registrado correctamente"
            )

            return redirect(
                'facturacion:crear_factura_servicio',
                cita_id=cita.id
            )

    else:
        form = HistorialServiciosForm()

    return render(request, 'citas/historial_servicio.html', {
        'cita': cita,
        'form': form
    })

@transaction.atomic
def crear_vacunacion(request, cita_id):

    cita = get_object_or_404(Cita, id=cita_id)

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    if not hasattr(usuario, 'veterinario'):
        messages.error(request, "No autorizado")
        return redirect('usuarios:login')

    if request.method == 'POST':
        form = VacunacionForm(request.POST)

        if form.is_valid():
            vacunacion = form.save(commit=False)

            vacunacion.cita = cita
            vacunacion.save()
            vacunacion.crear_historia_clinica()

            cita.estado = 'finalizada'
            cita.save()

            messages.success(request, "💉 Vacunación registrada correctamente")

            return redirect('facturacion:crear_factura_servicio', cita_id=cita.id)

    else:
        form = VacunacionForm()

    return render(request, 'citas/crear_vacunacion.html', {
        'form': form,
        'cita': cita
    })


def historial_servicios_mascota(request, mascota_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    mascota = get_object_or_404(Mascota, id=mascota_id)

    base_template = 'usuarios/base_panel.html'

    if hasattr(usuario, 'propietario'):

        if mascota.propietario != usuario.propietario:
            return redirect('usuarios:dashboard')

    elif hasattr(usuario, 'veterinario'):

        base_template = 'usuarios/base_veterinario.html'

    # 🔥 TODOS LOS SERVICIOS FINALIZADOS
    historial = Cita.objects.filter(
        mascota=mascota,
        estado='finalizada'
    ).select_related(
        'servicio',
        'veterinario'
    ).order_by('-fecha', '-hora')

    return render(request, 'citas/historial_servicios.html', {

        'mascota': mascota,
        'historial': historial,
        'base_template': base_template

    })

def historial_general_mascota(request, mascota_id):

    mascota = get_object_or_404(Mascota, id=mascota_id)

    consultas = Consulta.objects.filter(cita__mascota=mascota)
    vacunaciones = Vacunacion.objects.filter(cita__mascota=mascota)
    servicios = HistorialServicio.objects.filter(cita__mascota=mascota)
    tratamientos = Tratamiento.objects.filter(consulta__cita__mascota=mascota)

    return render(request, 'citas/historial_general.html', {
        'mascota': mascota,
        'consultas': consultas,
        'vacunaciones': vacunaciones,
        'servicios': servicios,
        'tratamientos': tratamientos,
    })