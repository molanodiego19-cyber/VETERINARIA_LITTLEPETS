from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from mascota.models import Mascota, Especie
from usuarios.forms_panel import MascotaForm
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import redirect, get_object_or_404


class MascotaListView(ListView):
    model = Mascota
    template_name = "panel/mascota/mascota_list.html"
    context_object_name = "mascotas"

    def get_queryset(self):
        mascotas = Mascota.objects.all()

        nombre = self.request.GET.get("nombre")
        color = self.request.GET.get("color")
        especie = self.request.GET.get("especie")
        sexo = self.request.GET.get("sexo")
        estado = self.request.GET.get("estado")

        if nombre:
            mascotas = mascotas.filter(nombre__icontains=nombre)

        if especie:
            mascotas = mascotas.filter(especie__id=especie)

        if color:
            mascotas = mascotas.filter(color=color)

        if sexo:
            mascotas = mascotas.filter(sexo=sexo)

        if estado:
            mascotas = mascotas.filter(estado=estado)

        return mascotas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["especies"] = Especie.objects.all()
        return context


class MascotaCreateView(CreateView):

    model = Mascota
    form_class = MascotaForm
    success_url = reverse_lazy("panel:panel_mascota_list")

    def get_template_names(self):

        rol = self.request.session.get("usuario_rol")

        if rol == "recepcionista":
            return ["panel/mascota/mascota_form_recepcionista.html"]

        return ["panel/mascota/mascota_form.html"]

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["es_recepcionista"] = (
            self.request.session.get("usuario_rol") == "recepcionista"
        )

        return context


class MascotaUpdateView(UpdateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "panel/mascota/mascota_form.html"
    success_url = reverse_lazy("panel:panel_mascota_list")


class MascotaDeleteView(View):
    def post(self, request, pk):
        mascota = get_object_or_404(Mascota, pk=pk)

        mascota.estado = "Inactiva"
        mascota.save()

        return redirect("panel:panel_mascota_list")


# -----------REPORTES-----------------------
def reporte_mascotas_pdf(request):
    # 🔎 OBTENER FILTROS DESDE LA URL
    especie = request.GET.get("especie")
    estado = request.GET.get("estado")
    sexo = request.GET.get("sexo")

    mascotas = Mascota.objects.all()

    # 🔥 FILTROS DINÁMICOS
    if especie:
        mascotas = mascotas.filter(especie__id=especie)

    if estado:
        mascotas = mascotas.filter(estado=estado)

    if sexo:
        mascotas = mascotas.filter(sexo=sexo)

    # 📄 TEMPLATE
    template = get_template("panel/mascota/mascota_pdf.html")
    context = {
        "mascotas": mascotas,
        "especie": especie,
        "estado": estado,
        "sexo": sexo,
    }

    html = template.render(context)

    # 🧾 GENERAR PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="reporte_mascotas.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF")
    return response
