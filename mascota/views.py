from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView ,UpdateView, ListView, CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from usuarios.views_panel import obtener_propietario
from .models import Mascota
from usuarios.models import Propietario
from mascota.models import Especie, Raza
from django.contrib import messages
from .forms import MascotaForm
from django.utils import timezone
from datetime import date

def registro_mascota_view(request):

    # =====================================================
    # 🔐 VALIDAR SESIÓN DE REGISTRO
    # =====================================================

    propietario_id = request.session.get("registro_propietario_id")

    if not propietario_id:
        return redirect("usuarios:registro")

    propietario = get_object_or_404(Propietario, id=propietario_id)

    # =====================================================
    # 📥 POST
    # =====================================================

    if request.method == "POST":

        if "omitir" in request.POST:
            # 🧹 LIMPIAR SESIÓN
            request.session.pop("registro_propietario_id", None)

            # 👤 INICIAR SESIÓN
            request.session["usuario_id"] = propietario.usuario.id

            # ✅ MENSAJE
            messages.success(
                request, "🐾 Registro completado. Puedes agregar mascotas después."
            )

            # 🔀 REDIRECCIÓN
            return redirect("usuarios:dashboard")

        # ✅ USAR EL FORMULARIO
        form = MascotaForm(request.POST, request.FILES)

        # =================================================
        # ✅ VALIDAR FORMULARIO
        # =================================================

        if form.is_valid():

            # =============================================
            # 🐾 CREAR OBJETO SIN GUARDAR
            # =============================================

            mascota = form.save(commit=False)

            # =============================================
            # 🔗 ASIGNAR PROPIETARIO
            # =============================================

            mascota.propietario = propietario

            # =============================================
            # 💾 GUARDAR
            # =============================================

            mascota.save()

            # =============================================
            # 🧹 LIMPIAR SESIÓN
            # =============================================

            request.session.pop("registro_propietario_id", None)

            # =============================================
            # 👤 INICIAR SESIÓN
            # =============================================

            request.session["usuario_id"] = propietario.usuario.id

            # =============================================
            # ✅ MENSAJE
            # =============================================

            messages.success(request, "🐾 Mascota registrada correctamente")

            # =============================================
            # 🔀 REDIRECCIÓN
            # =============================================

            return redirect("usuarios:dashboard")

        # =================================================
        # ❌ SI HAY ERRORES
        # =================================================

        especies = Especie.objects.all()

        return render(
            request,
            "usuarios/registro_mascota.html",
            {"form": form, "especies": especies, "today": date.today().isoformat()},
        )

    # =====================================================
    # 📄 GET
    # =====================================================

    form = MascotaForm()

    especies = Especie.objects.all()

    return render(
        request,
        "usuarios/registro_mascota.html",
        {
            "form": form,
            "especies": especies,
            # 🔥 PARA EL max=""
            "today": date.today().isoformat(),
        },
    )

class MascotaListView(ListView):
    model = Mascota

    def get_template_names(self):

        usuario_id = self.request.session.get("usuario_id")

        if usuario_id:
            from usuarios.models import Usuario

            try:
                usuario = Usuario.objects.get(id=usuario_id)

                # Recepcionista
                if hasattr(usuario, "recepcionista"):
                    return ["panel/mascota/mascota_recepcionista.html"]

            except Usuario.DoesNotExist:
                pass

        # Propietario por defecto
        return ["mascotas/mascotas_list.html"]

    def get_queryset(self):

        usuario_id = self.request.session.get("usuario_id")

        if usuario_id:
            from usuarios.models import Usuario

            try:
                usuario = Usuario.objects.get(id=usuario_id)

                # Recepcionista ve todas las mascotas
                if hasattr(usuario, "recepcionista"):
                    return Mascota.objects.all().order_by("nombre")

            except Usuario.DoesNotExist:
                pass

        # Propietario solo ve las suyas
        propietario = obtener_propietario(self.request)

        if not propietario:
            return Mascota.objects.none()

        return Mascota.objects.filter(propietario=propietario, estado="ACTIVO")


# -------------OBTENER RAZAS------------------


def cargar_razas(request):
    especie_id = request.GET.get("especie_id")
    razas = Raza.objects.filter(tipo_especie_id=especie_id).values("id", "nombre")
    return JsonResponse(list(razas), safe=False)



class MascotaCreateView(CreateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascotas/mascota_form.html"
    success_url = reverse_lazy("mascota:mascotas")

    def form_valid(self, form):
        propietario = obtener_propietario(self.request)
        form.instance.propietario = propietario
        return super().form_valid(form)

def cargar_razas(request):
    especie_id = request.GET.get("especie_id")

    if not especie_id:
        return JsonResponse([], safe=False)

    razas = Raza.objects.filter(tipo_especie_id=especie_id).values("id", "nombre")
    return JsonResponse(list(razas), safe=False)

class MascotaUpdateView(UpdateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascotas/mascota_form.html"
    success_url = reverse_lazy("mascota:mascotas")

    def get_queryset(self):
        propietario = obtener_propietario(self.request)
        return Mascota.objects.filter(propietario=propietario)


def eliminar_mascota(request, pk):
    propietario = obtener_propietario(request)

    mascota = get_object_or_404(Mascota, pk=pk, propietario=propietario)

    mascota.estado = "Inactivo"
    mascota.save()

    return redirect("mascota:mascotas")


class MascotaDetailView(DetailView):
    model = Mascota
    template_name = "mascotas/mascota_detalle.html"

    def get_queryset(self):
        propietario = obtener_propietario(self.request)
        return Mascota.objects.filter(propietario=propietario)
