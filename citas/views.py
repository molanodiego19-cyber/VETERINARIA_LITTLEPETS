from datetime import datetime, timedelta, date
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from mascota.forms import MascotaForm
from mascota.models import Mascota, Raza
from notificacion.services import crear_notificacion
from usuarios.forms import PropietarioCompletoForm
from usuarios.models import Usuario, Veterinario
from .utils import generar_horarios_disponibles, veterinario_disponible
from usuarios.models import Propietario
from .forms import (
    CategoriaServiciosForm,
    CitaForm,
    CitaRecepcionistaForm,
    ConsultaCompletaForm,
    ConsultaForm,
    HistoriaClinicaForm,
    MedicamentoForm,
    ReagendarCitaForm,
    ServicioForm,
    TratamientoForm,
    VacunacionForm,
)

from .models import (
    CategoriaServicios,
    Cita,
    Consulta,
    HistoriaClinica,
    Medicamento,
    Servicio,
    Tratamiento,
    Vacunacion,
    Vacuna
)


def index(request):
    return render(request, "index.html")


def crear_objeto(request, form_class, template):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = form_class()
    return render(request, template, {"form": form})


# ---------------------------------------------------------------
# VACUNAS AGENDADAS
# ------------------------------------------------------------
def vacunas_agendadas(request):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("login")

    citas_vacunas = (
        Cita.objects.filter(servicio__nombre__icontains="Vacuna")
        .select_related("mascota", "servicio", "vacuna")
        .order_by("fecha", "hora")
    )

    context = {"citas_vacunas": citas_vacunas}

    return render(request, "citas/vacunas_agendadas.html", context)


# ----------------------------------------------------------------------------------------------------------------------------------


def consulta(request):
    return crear_objeto(request, ConsultaForm, "panel/form.html")


def historiaclinica(request):
    return crear_objeto(request, HistoriaClinicaForm, "panel/form.html")


def categoriaservicio(request):
    return crear_objeto(request, CategoriaServiciosForm, "panel/form.html")


def servicio(request):
    return crear_objeto(request, ServicioForm, "panel/form.html")


def medicamento(request):
    return crear_objeto(request, MedicamentoForm, "panel/form.html")


def tratamiento(request):
    return crear_objeto(request, TratamientoForm, "panel/form.html")


def eliminar_consulta(request, pk):
    obj = get_object_or_404(Consulta, pk=pk)
    if request.method == "POST":
        obj.delete()
    return redirect("dashboard")


def eliminar_historiaclinica(request, pk):
    obj = get_object_or_404(HistoriaClinica, pk=pk)
    if request.method == "POST":
        obj.delete()
    return redirect("dashboard")


def eliminar_categoriaservicio(request, pk):
    obj = get_object_or_404(CategoriaServicios, pk=pk)
    if request.method == "POST":
        obj.delete()
    return redirect("dashboard")


def eliminar_servicio(request, pk):
    obj = get_object_or_404(Servicio, pk=pk)
    if request.method == "POST":
        obj.delete()
    return redirect("dashboard")


def eliminar_tratamiento(request, pk):
    obj = get_object_or_404(Tratamiento, pk=pk)
    if request.method == "POST":
        obj.delete()
    return redirect("dashboard")


def editar_consulta(request, pk):
    obj = get_object_or_404(Consulta, pk=pk)
    if request.method == "POST":
        form = ConsultaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ConsultaForm(instance=obj)
    return render(request, "panel/form.html", {"form": form})


def editar_historiaclinica(request, pk):
    obj = get_object_or_404(HistoriaClinica, pk=pk)
    if request.method == "POST":
        form = HistoriaClinicaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = HistoriaClinicaForm(instance=obj)
    return render(request, "panel/form.html", {"form": form})


def editar_categoriaservicio(request, pk):
    obj = get_object_or_404(CategoriaServicios, pk=pk)
    if request.method == "POST":
        form = CategoriaServiciosForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = CategoriaServiciosForm(instance=obj)
    return render(request, "panel/form.html", {"form": form})


def editar_servicio(request, pk):
    obj = get_object_or_404(Servicio, pk=pk)
    if request.method == "POST":
        form = ServicioForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = ServicioForm(instance=obj)
    return render(request, "panel/form.html", {"form": form})


def editar_medicamento(request, pk):
    obj = get_object_or_404(Medicamento, pk=pk)
    if request.method == "POST":
        form = MedicamentoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = MedicamentoForm(instance=obj)
    return render(request, "panel/form.html", {"form": form})


def editar_tratamiento(request, pk):
    obj = get_object_or_404(Tratamiento, pk=pk)
    if request.method == "POST":
        form = TratamientoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = TratamientoForm(instance=obj)
    return render(request, "panel/form.html", {"form": form})

# =========================================================
# FUNCIÓN REUTILIZABLE PARA FILTRAR CITAS
# =========================================================


def filtrar_citas(request):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return Cita.objects.none()

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Cita.objects.none()

    # 🔐 SOLO PROPIETARIOS VEN SUS CITAS
    if hasattr(usuario, "propietario"):
        citas = Cita.objects.filter(dueño=usuario.propietario)

    # 🔐 VETERINARIO VE SUS CITAS
    elif hasattr(usuario, "veterinario"):
        citas = Cita.objects.filter(veterinario=usuario.veterinario)

    else:
        return Cita.objects.none().order_by("fecha", "hora")

    # =========================
    # FILTROS
    # =========================

    estado = request.GET.get("estado")
    fecha = request.GET.get("fecha")
    servicio = request.GET.get("servicio")
    veterinario = request.GET.get("veterinario")

    if estado:
        citas = citas.filter(estado=estado)

    if fecha:
        citas = citas.filter(fecha=fecha)

    if servicio:
        citas = citas.filter(servicio_id=servicio)

    if veterinario:
        citas = citas.filter(veterinario_id=veterinario)

    return citas.order_by("-fecha", "-hora")


class CitaCreateView(CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/cita_form.html"
    success_url = reverse_lazy("citas:listar")

    def get_template_names(self):

        rol = self.request.session.get("usuario_rol")

        if rol == "recepcionista":
            return ["citas/cita_form_recepcionista.html"]

        return ["citas/cita_form.html"]

    def form_valid(self, form):

        propietario_id_url = self.request.GET.get("propietario_id")

        if propietario_id_url:
            propietario = get_object_or_404(Propietario, id=propietario_id_url)

            usuario_notificar = propietario.usuario
        else:

            usuario_id = self.request.session.get("usuario_id")
            if not usuario_id:
                form.add_error(None, "❌ Usuario no autenticado")
                return self.form_invalid(form)

            usuario_notificar = get_object_or_404(Usuario, id=usuario_id)
            if not hasattr(usuario_notificar, "propietario"):
                form.add_error(None, "❌ Usuario no es propietario")
                return self.form_invalid(form)
            propietario = usuario_notificar.propietario

        # -------------------------------
        # 📅 Lógica de asignación
        # -------------------------------
        fecha = form.cleaned_data["fecha"]
        hora = form.cleaned_data["hora"]
        servicio = form.cleaned_data["servicio"]

        # =====================================================
        # ⏰ VALIDAR ANTICIPACIÓN DE 2 HORAS
        # =====================================================

        # Combinar fecha y hora de la cita
        fecha_hora_cita = datetime.combine(fecha, hora)

        # Convertir a timezone local
        fecha_hora_cita = timezone.make_aware(
            fecha_hora_cita, timezone.get_current_timezone()
        )

        # Hora actual + 2 horas
        limite = timezone.now() + timedelta(hours=1)

        # Validar
        if fecha_hora_cita < limite:
            form.add_error(
                None, "❌ Las citas deben agendarse con mínimo 1 horas de anticipación"
            )
            return self.form_invalid(form)

        veterinarios = Veterinario.objects.filter(disponible=True, servicios=servicio)

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
            "nombre": cita.dueño.nombre,
            "mascota": cita.mascota.nombre,
            "fecha": cita.fecha,
            "hora": cita.hora,
            "servicio": cita.servicio.nombre,
            "veterinario": cita.veterinario.nombre,
        }

        crear_notificacion(
            usuario=usuario_notificar,
            plantilla_nombre="cita_agendada",
            cita=cita,
            contexto=contexto,
        )

        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    # ------------------FECHA DESDE EL VIEW----
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = date.today().isoformat()  # 🔥 clave
        return context


# ------------LISTAR CITAS---------------------------
class CitasListView(ListView):

    model = Cita
    template_name = "citas/cita_list.html"

    context_object_name = "citas"

    # 🔐 PROTECCIÓN
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("usuario_id"):
            return redirect("usuarios:login")
        return super().dispatch(request, *args, **kwargs)

    # ==========================================
    # QUERYSET FILTRADO
    # ==========================================

    def get_queryset(self):

        citas_filtradas = filtrar_citas(self.request)

        return citas_filtradas.exclude(servicio__nombre__icontains="Vacuna")

    # ==========================================
    # CONTEXTO
    # ==========================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["servicios"] = Servicio.objects.all()

        context["veterinarios"] = Veterinario.objects.all()

        context["estados"] = Cita.ESTADOS

        return context


# -------------CANCELAR CITAS-------------------------------------


def cancelar_cita(request, pk):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=usuario_id)

    cita = get_object_or_404(Cita, pk=pk)

    # =====================================
    # EVITAR CANCELAR DOS VECES
    # =====================================

    if cita.estado == "cancelada":

        messages.warning(request, "La cita ya se encuentra cancelada.")

        if usuario.rol == "recepcionista":
            return redirect("panel:panel_cita_list")

        return redirect("citas:listar")

    # =====================================
    # EVITAR MODIFICAR CITAS FINALIZADAS
    # =====================================

    if cita.estado in ["atendida", "facturada"]:

        messages.error(request, "No es posible cancelar una cita ya atendida.")

        if usuario.rol == "recepcionista":
            return redirect("panel:panel_cita_list")

        return redirect("citas:listar")

    # =====================================
    # VALIDAR TIEMPO DE CANCELACIÓN
    # =====================================

    fecha_hora_cita = timezone.make_aware(
        datetime.combine(cita.fecha, cita.hora), timezone.get_current_timezone()
    )

    limite_cancelacion = fecha_hora_cita + timedelta(minutes=30)

    if timezone.now() > limite_cancelacion:

        cita.estado = "no_asistio"
        cita.save(update_fields=["estado"])

        messages.error(
            request,
            "Han pasado más de 30 minutos desde la hora de la cita. Se marcó como No Asistió.",
        )

        if usuario.rol == "recepcionista":
            return redirect("panel:panel_cita_list")

        return redirect("citas:listar")

    # =====================================
    # CANCELAR CITA
    # =====================================

    cita.estado = "cancelada"
    cita.save(update_fields=["estado"])

    # =====================================
    # NOTIFICACIÓN
    # =====================================

    contexto = {
        "nombre": cita.dueño.nombre,
        "mascota": cita.mascota.nombre,
        "fecha": cita.fecha,
        "hora": cita.hora,
        "servicio": cita.servicio.nombre,
        "veterinario": (cita.veterinario.nombre if cita.veterinario else "No asignado"),
    }

    crear_notificacion(
        usuario=cita.dueño.usuario,
        plantilla_nombre="cita_cancelada",
        cita=cita,
        contexto=contexto,
    )

    messages.success(request, "✅ Cita cancelada correctamente.")

    if usuario.rol == "recepcionista":
        return redirect("panel:panel_cita_list")

    return redirect("citas:listar")


# ------------------REAGENDAR---------------------------------
class CitaUpdateView(UpdateView):

    model = Cita
    form_class = ReagendarCitaForm
    template_name = "citas/reagendar_cita.html"
    success_url = reverse_lazy("citas:listar")

    def form_valid(self, form):

        cita = form.instance  # 🔥 AQUÍ está lo nuevo del form

        # unir fecha + hora del FORM (no del DB)
        fecha_hora = datetime.combine(cita.fecha, cita.hora)

        fecha_hora = timezone.make_aware(fecha_hora)

        ahora = timezone.now()

        # regla 12 horas
        if fecha_hora - ahora < timedelta(hours=12):
            form.add_error(
                None,
                "❌ Solo puedes reagendar con mínimo 12 horas de anticipación"
            )
            return self.form_invalid(form)

        messages.success(self.request, "✅ Cita reagendada correctamente")

        return super().form_valid(form)

# --------------HORARIO DISPONIBLE----------------------------
def horarios_disponibles(request):

    fecha_str = request.GET.get("fecha")
    servicio_id = request.GET.get("servicio")

    if not fecha_str or not servicio_id:
        return JsonResponse([], safe=False)

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    servicio = Servicio.objects.get(id=servicio_id)

    veterinarios = Veterinario.objects.filter(disponible=True, servicios=servicio)

    # filtro por especialidad
    if servicio.especialista_required:
        veterinarios = veterinarios.filter(especialidad=servicio.especialista_required)

    horarios = generar_horarios_disponibles(fecha, servicio, veterinarios)

    return JsonResponse(horarios, safe=False)


# -------------------------CALENDARIO--------------
def eventos_calendario(request):

    usuario_id = request.session.get("usuario_id")
    usuario = Usuario.objects.get(id=usuario_id)

    if hasattr(usuario, "propietario"):
        citas = Cita.objects.filter(
            dueño=usuario.propietario, estado__in=["pendiente", "confirmada"]
        )
    elif hasattr(usuario, "veterinario"):
        citas = Cita.objects.filter(
            veterinario=usuario.veterinario, estado__in=["pendiente", "confirmada"]
        )
    else:
        citas = Cita.objects.none()

    eventos = []

    for cita in citas:
        inicio = datetime.combine(cita.fecha, cita.hora)
        fin = inicio + timedelta(minutes=cita.servicio.duracion_minutos)

        eventos.append(
            {
                "title": "Ocupado",
                "start": inicio.isoformat(),
                "end": fin.isoformat(),
                "color": "red",
            }
        )

    return JsonResponse(eventos, safe=False)


# -----proteccion


def dispatch(self, request, *args, **kwargs):

    if not request.session.get("usuario_id"):
        return redirect("usuarios:login")

    return super().dispatch(request, *args, **kwargs)


# -----iniciar consultas


def iniciar_consulta(request, cita_id):

    cita = get_object_or_404(Cita, id=cita_id)

    if cita.estado in ["cancelada", "no_asistio", "atendida"]:
        messages.warning(request, "Esta cita no puede iniciarse")
        return redirect("usuarios:citas_veterinario")

    cita.estado = "en_proceso"
    cita.save()

    #CREAR CONSULTA AL INICIAR

    Consulta.objects.create(
        cita=cita,
        anamnesis="",
        examen_fisico="",
        diagnostico_presuntivo="",
        diagnostico_definitivo="",
        plan_terapeutico="",
        observaciones="",
    )

    categoria = cita.servicio.categoria.nombre_categoria.lower()

    categorias_vacunacion = [
        "vacuna",
        "vacunación",
        "vacunacion",
        "inmunización",
        "inmunizacion",
    ]

    # 💉 Si es vacunación
    if categoria in categorias_vacunacion:
        return redirect(
            "citas:crear_vacunacion",
            cita_id=cita.id
        )

    # 🩺 Cualquier otro servicio
    return redirect(
        "citas:crear_consulta",
        cita_id=cita.id
    )


class CrearConsultaView(CreateView):
    model = Consulta
    form_class = ConsultaCompletaForm
    template_name = 'citas/crear_consulta.html'

    def get_initial(self):
        cita = get_object_or_404(Cita, id=self.kwargs.get('cita_id'))
        return {
            'peso_en_consulta': cita.mascota.peso_kg if cita.mascota.peso_kg else None,
            'observaciones': cita.notas_adicionales,
            'mascota': cita.mascota,
            'veterinario': cita.veterinario,
        }

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        self.object = None

        accion = request.POST.get("accion")

        cita = get_object_or_404(Cita, id=self.kwargs.get("cita_id"))

        form = self.get_form()

        if not form.is_valid():
            return self.form_invalid(form)

        # ==========================
        # GUARDAR CONSULTA
        # ==========================

        consulta = get_object_or_404(
        Consulta,
        cita=cita
        )

        consulta.fecha_fin = timezone.now()

        consulta.anamnesis = form.cleaned_data["anamnesis"]
        consulta.examen_fisico = form.cleaned_data["examen_fisico"]

        consulta.diagnostico_presuntivo = form.cleaned_data["diagnostico_presuntivo"]
        consulta.diagnostico_definitivo = form.cleaned_data["diagnostico_definitivo"]

        consulta.plan_terapeutico = form.cleaned_data["plan_terapeutico"]
        consulta.observaciones = form.cleaned_data["observaciones"]

        consulta.peso_en_consulta = form.cleaned_data["peso_en_consulta"]

        consulta.temperatura = form.cleaned_data["temperatura"]

        consulta.frecuencia_cardiaca = form.cleaned_data["frecuencia_cardiaca"]

        consulta.frecuencia_respiratoria = form.cleaned_data["frecuencia_respiratoria"]

 
        consulta.save()

        consulta.crear_historia_clinica()
        
        # ==========================
        # VACUNACIÓN OPCIONAL
        # ==========================

        vacuna_id = request.POST.get("vacuna_id")

        if vacuna_id:

            vacuna = get_object_or_404(
                Vacuna,
                id=vacuna_id
            )

            vacunacion = Vacunacion.objects.create(
                cita=cita,
                vacuna=vacuna,
                numero_dosis=request.POST.get("numero_dosis") or 1,
                proxima_dosis=request.POST.get("proxima_dosis") or None,
                observaciones=request.POST.get(
                    "observaciones_vacuna"
                ),
                peso_actual=consulta.peso_en_consulta
            )

            vacunacion.crear_historia_clinica()

        # ==========================
        # ESTADO CITA
        # ==========================

        cita.estado = "atendida"
        cita.save(update_fields=["estado"])

        # ==========================
        # SOLO CONSULTA
        # ==========================

        if accion != "tratamiento":

            messages.success(
                request,
                "✅ Consulta guardada correctamente."
            )

            return redirect("usuarios:citas_veterinario")

        # ==========================
        # CONSULTA + TRATAMIENTO
        # ==========================

        messages.success(
            request,
            "✅ Consulta guardada correctamente."
        )

        return redirect(
            "citas:crear_tratamiento",
            consulta_id=consulta.id
        )

    def form_invalid(self, form):
        messages.error(self.request, "❌ Error al guardar la consulta.")

        return self.render_to_response(self.get_context_data(form=form))


def historia_clinica_mascota(request, mascota_id):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=usuario_id)

    mascota = get_object_or_404(Mascota, id=mascota_id)

    base_template = "usuarios/base_panel.html"

    if hasattr(usuario, "propietario"):

        if mascota.propietario != usuario.propietario:
            return redirect("usuarios:dashboard")

    elif hasattr(usuario, "veterinario"):

        base_template = "usuarios/base_veterinario.html"

    else:
        return redirect("usuarios:login")

    # ================= CONSULTAS =================

    consultas = (
        HistoriaClinica.objects.filter(
            mascota=mascota,
            tipo_registro="consulta"
        )
        .select_related("veterinario", "cita")
        .order_by("-fecha_consulta")
    )

    vacunaciones = (
        Vacunacion.objects.filter(
            cita__mascota=mascota
        )
        .select_related(
            "vacuna",
            "cita",
            "cita__veterinario"
        )
        .order_by("-fecha_aplicacion")
    )

    tratamientos = (
        Tratamiento.objects.filter(
            consulta__cita__mascota=mascota
        )
        .select_related(
            "consulta",
            "consulta__cita",
            "veterinario"
        )
        .order_by("-fecha_creacion")
    )

    return render(
        request,
        "citas/historia_mascota.html",
        {
            "mascota": mascota,
            "consultas": consultas,
            "vacunaciones": vacunaciones,
            "tratamientos": tratamientos,
            "base_template": base_template,
        },
    )


def crear_tratamiento(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)

    # 🔐 validar sesión
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        messages.error(request, "Sesión no válida")
        return redirect("login")

    usuario = Usuario.objects.get(id=usuario_id)

    if not hasattr(usuario, "veterinario"):
        messages.error(request, "No autorizado")
        return redirect("login")

    veterinario = usuario.veterinario

    if request.method == "POST":
        form = TratamientoForm(request.POST)

        if form.is_valid():
            tratamiento = form.save(commit=False)

            # 🔥 asignaciones automáticas
            tratamiento.consulta = consulta
            tratamiento.veterinario = veterinario
            tratamiento.fecha_creacion = timezone.now()

            tratamiento.save()

            messages.success(request, "💊 Tratamiento creado correctamente")
            return redirect("usuarios:citas_veterinario")

    else:
        form = TratamientoForm()

    return render(
        request, "citas/crear_tratamiento.html", {"form": form, "consulta": consulta}
    )

@transaction.atomic
def crear_vacunacion(request, cita_id):

    cita = get_object_or_404(Cita, id=cita_id)

    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=usuario_id)

    if not hasattr(usuario, "veterinario"):
        messages.error(request, "No autorizado")
        return redirect("usuarios:login")

    if request.method == "POST":
        form = VacunacionForm(request.POST)

        if form.is_valid():

            vacunacion = form.save(commit=False)

            vacunacion.cita = cita
            vacunacion.save()

            vacunacion.crear_historia_clinica()

            cita.estado = "atendida"

            cita.save()

            messages.success(request, "💉 Vacunación registrada correctamente")

            return redirect("usuarios:citas_veterinario")

    else:
        form = VacunacionForm()

        return render(
            request,
            "citas/crear_vacunacion.html",
            {
                "form": form,
                "cita": cita,
                "servicios": Servicio.objects.filter(
    activo=True,
    nombre="Consulta General"
),
            },
        )


def historial_servicios_mascota(request, mascota_id):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=usuario_id)

    mascota = get_object_or_404(Mascota, id=mascota_id)

    base_template = "usuarios/base_panel.html"

    if hasattr(usuario, "propietario"):

        if mascota.propietario != usuario.propietario:
            return redirect("usuarios:dashboard")

    elif hasattr(usuario, "veterinario"):

        base_template = "usuarios/base_veterinario.html"

    # 🔥 TODOS LOS SERVICIOS FINALIZADOS
    historial = (
        Cita.objects.filter(mascota=mascota, estado="finalizada")
        .select_related("servicio", "veterinario")
        .order_by("-fecha", "-hora")
    )

    return render(
        request,
        "citas/historial_servicios.html",
        {"mascota": mascota, "historial": historial, "base_template": base_template},
    )


def historial_general_mascota(request, mascota_id):

    mascota = get_object_or_404(Mascota, id=mascota_id)

    consultas = Consulta.objects.filter(cita__mascota=mascota)
    vacunaciones = Vacunacion.objects.filter(cita__mascota=mascota)
    tratamientos = Tratamiento.objects.filter(consulta__cita__mascota=mascota)

    return render(
        request,
        "citas/historial_general.html",
        {
            "mascota": mascota,
            "consultas": consultas,
            "vacunaciones": vacunaciones,
            "tratamientos": tratamientos,
        },
    )

def cargar_razas(request):
    especie_id = request.GET.get("especie_id")

    if not especie_id:
        return JsonResponse([], safe=False)

    razas = Raza.objects.filter(tipo_especie_id=especie_id).values("id", "nombre")

    return JsonResponse(list(razas), safe=False)
# ===============================
# CREAR CITA RECEPCIONISTA
# ===========================

class AgendarCitaRecepcionistaView(TemplateView):
    template_name = "citas/cita_form_recepcionista.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["propietario_form"] = PropietarioCompletoForm(prefix="propietario")
        context["mascota_form"] = MascotaForm(prefix="mascota")
        # 🌟 Usamos el nuevo formulario plano para recepcionista
        context["cita_form"] = CitaRecepcionistaForm(prefix="cita")
        context["today"] = date.today().isoformat()
        return context

    def post(self, request, *args, **kwargs):
        propietario_form = PropietarioCompletoForm(
            request.POST, request.FILES, prefix="propietario"
        )
        mascota_form = MascotaForm(request.POST, request.FILES, prefix="mascota")
        # 🌟 Usamos el nuevo formulario plano para recepcionista aquí también
        cita_form = CitaRecepcionistaForm(data=request.POST, prefix="cita")

        # Ahora el is_valid() pasará fluidamente como la seda 🚀
        if (
            propietario_form.is_valid()
            and mascota_form.is_valid()
            and cita_form.is_valid()
        ):
            try:
                with transaction.atomic():
                    # 1. Guardar Propietario
                    propietario = propietario_form.save()

                    # 2. Guardar Mascota asociada al nuevo dueño
                    mascota_real = mascota_form.save(commit=False)
                    mascota_real.propietario = propietario
                    mascota_real.save()

                    # 3. Extraer datos limpios de la Cita
                    fecha = cita_form.cleaned_data["fecha"]
                    hora = cita_form.cleaned_data["hora"]
                    servicio = cita_form.cleaned_data["servicio"]
                    vacuna = cita_form.cleaned_data.get("vacuna")
                    motivo_consulta = cita_form.cleaned_data.get("motivo_consulta", "")

                    # --- Validación de Tiempo ---
                    fecha_hora_cita = datetime.combine(fecha, hora)
                    fecha_hora_cita = timezone.make_aware(
                        fecha_hora_cita, timezone.get_current_timezone()
                    )
                    if fecha_hora_cita < timezone.now() + timedelta(hours=1):
                        raise ValueError(
                            "❌ Las citas deben agendarse con mínimo 1 hora de anticipación"
                        )

                    # --- Buscar Veterinario Disponible ---
                    veterinarios = Veterinario.objects.filter(
                        disponible=True, servicios=servicio
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
                        raise ValueError(
                            "❌ No hay veterinarios disponibles para este servicio en ese horario"
                        )

                    # 4. CREAR LA CITA REAL ASIGNANDO LAS NUEVAS INSTANCIAS
                    # (Nota: Verifica si en tu modelo Cita se llama 'dueño' o 'propietario')
                    cita = Cita(
                        fecha=fecha,
                        hora=hora,
                        servicio=servicio,
                        vacuna=vacuna,
                        motivo_consulta=motivo_consulta,
                        mascota=mascota_real,
                        dueño=propietario,
                        veterinario=veterinario_asignado,
                    )
                    cita.save()

                    # 5. Enviar Notificación
                    contexto = {
                        "nombre": propietario.nombre,
                        "mascota": mascota_real.nombre,
                        "fecha": cita.fecha,
                        "hora": cita.hora,
                        "servicio": cita.servicio.nombre,
                        "veterinario": veterinario_asignado.nombre,
                    }
                    crear_notificacion(
                        usuario=propietario.usuario,
                        plantilla_nombre="cita_agendada",
                        cita=cita,
                        contexto=contexto,
                    )

                messages.success(
                    request,
                    "¡Todo guardado con éxito! Cliente, mascota y cita registrados.",
                )
                return redirect("panel:panel_cita_list")

            except ValueError as e:
                cita_form.add_error(None, str(e))
            except Exception as e:
                cita_form.add_error(None, f"Error en el guardado: {e}")

        return render(
            request,
            self.template_name,
            {
                "propietario_form": propietario_form,
                "mascota_form": mascota_form,
                "cita_form": cita_form,
                "today": date.today().isoformat(),
            },
        )


# ===================
# CAMBIAR ESTADO
# =====================

def confirmar_cita_recepcionista(request, cita_id):
    if request.method == "POST":
        # Buscamos la cita o devolvemos un 404 si no existe
        cita = get_object_or_404(Cita, id=cita_id)

        # Cambiamos el estado (Ajusta 'pendiente' y 'confirmada' según tus choices reales)
        if cita.estado == "pendiente":
            cita.estado = "confirmada"
            cita.save()
            messages.success(
                request,
                f"¡La cita de {cita.mascota.nombre} ha sido confirmada con éxito!",
            )
        else:
            messages.warning(
                request, "Esta cita ya no está pendiente o ya fue procesada."
            )

    # Redirecciona a la misma lista de citas de la recepcionista
    return redirect("panel:panel_cita_list")


# =====================================================
# CREAR CITA CON USUARIO EXISTENTE DESDE RECEPCIONISTA
# =================================================
class CitaRecepcionistaCreateView(CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/form_propietario.html"  # Tu template para recepción
    success_url = reverse_lazy("panel:panel_cita_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request

        propietario_id = self.request.GET.get(
            "propietario_id"
        ) or self.request.POST.get("propietario_id")

        if propietario_id:
            kwargs["propietario_id"] = propietario_id

        return kwargs

    def form_valid(self, form):
        # 1. Recuperamos el ID del propietario desde el input hidden del formulario
        propietario_id = self.request.POST.get("propietario_id")

        if not propietario_id:
            form.add_error(None, "❌ No se ha seleccionado un propietario válido.")
            return self.form_invalid(form)

        propietario = get_object_or_404(Propietario, id=propietario_id)
        usuario_notificar = propietario.usuario

        # 2. Captura de campos de fecha y hora directamente desde el POST
        # (Obligatorio porque provienen de inputs ocultos gestionados por tu JS)
        fecha_str = self.request.POST.get("fecha")
        hora_str = self.request.POST.get("hora")
        servicio = form.cleaned_data.get("servicio")

        if not fecha_str or not hora_str:
            form.add_error(
                None, "❌ Debes seleccionar una fecha y un horario de la lista."
            )
            return self.form_invalid(form)

        try:
            # Convertimos los strings del JS a objetos Python correspondientes
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora = datetime.strptime(hora_str, "%H:%M").time()
        except ValueError:
            form.add_error(None, "❌ El formato de la fecha u hora es inválido.")
            return self.form_invalid(form)

        # 3. Asignación automática de Veterinario (Tu lógica original)
        veterinarios = Veterinario.objects.filter(disponible=True, servicios=servicio)
        if servicio.especialista_required:
            veterinarios = veterinarios.filter(
                especialidad=servicio.especialista_required
            )

        veterinario_asignado = None
        for vet in veterinarios:
            if veterinario_disponible(
                vet, fecha, hora, servicio
            ):  # Tu función externa de validación
                veterinario_asignado = vet
                break

        if not veterinario_asignado:
            form.add_error(
                None, "❌ No hay veterinarios disponibles para este servicio y horario."
            )
            return self.form_invalid(form)

        # 4. Guardar datos validados y recuperados en la instancia del modelo Cita
        form.instance.fecha = fecha
        form.instance.hora = hora
        form.instance.veterinario = veterinario_asignado
        form.instance.dueño = propietario

        response = super().form_valid(form)

        # 5. Envío de Notificación al Propietario de la mascota
        cita = self.object
        contexto = {
            "nombre": cita.dueño.nombre,
            "mascota": cita.mascota.nombre,
            "fecha": cita.fecha,
            "hora": cita.hora,
            "servicio": cita.servicio.nombre,
            "veterinario": cita.veterinario.nombre,
        }

        crear_notificacion(
            usuario=usuario_notificar,
            plantilla_nombre="cita_agendada",
            cita=cita,
            contexto=contexto,
        )

        return response

    def get_context_data(self, **kwargs):
        """Agrega variables adicionales al contexto del template"""
        context = super().get_context_data(**kwargs)
        context["today"] = date.today().isoformat()

        # 🔍 Buscamos al propietario para poder pintar su información en el HTML
        propietario_id = self.request.GET.get(
            "propietario_id"
        ) or self.request.POST.get("propietario_id")
        if propietario_id:
            context["propietario_seleccionado"] = get_object_or_404(
                Propietario, id=propietario_id
            )

        return context
