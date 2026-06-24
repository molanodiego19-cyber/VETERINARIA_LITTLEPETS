from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from usuarios.models import Veterinario
from usuarios.forms import VeterinarioCompletoForm, VeterinarioUpdateForm
from django.http import JsonResponse
from citas.models import Servicio
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
# EXCEL
import openpyxl
from veterinarioapp.models import Especialidad
from usuarios.models import Usuario

# =====================================================
# FILTRO REUTILIZABLE
# =====================================================


def filtrar_veterinarios(request):

    veterinarios = Veterinario.objects.select_related("usuario").all().order_by("-id")

    nombre = request.GET.get("nombre")
    if nombre:
        veterinarios = veterinarios.filter(nombre__icontains=nombre)

    documento = request.GET.get("documento")
    if documento:
        veterinarios = veterinarios.filter(documento__icontains=documento)

    especialidad_id = request.GET.get("especialidad_id")
    if especialidad_id:
        veterinarios = veterinarios.filter(especialidad_id=especialidad_id)

    estado = request.GET.get("estado")
    if estado:
        veterinarios = veterinarios.filter(usuario__estado=estado)

    return veterinarios


class VeterinarioListView(ListView):
    model = Veterinario
    template_name = "panel/veterinario/list.html"
    context_object_name = "veterinarios"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["veterinarios"] = filtrar_veterinarios(self.request)
        context["especialidades"] = Especialidad.objects.all()

        context["estados"] = [
            ("activo", "Activo"),
            ("inactivo", "Inactivo"),
        ]

        return context


class VeterinarioCreateView(CreateView):
    model = Veterinario
    form_class = VeterinarioCompletoForm
    template_name = "panel/veterinario/form.html"
    success_url = reverse_lazy("panel:panel_veterinario_list")


class VeterinarioUpdateView(UpdateView):
    model = Veterinario
    form_class = VeterinarioUpdateForm
    template_name = "panel/veterinario/form.html"
    success_url = reverse_lazy("panel:panel_veterinario_list")


class VeterinarioDeleteView(View):
    def post(self, request, pk):
        veterinario = get_object_or_404(Veterinario, pk=pk)

        veterinario.usuario.estado = Usuario.Estado.INACTIVO
        veterinario.usuario.save()

        return redirect("panel:panel_veterinario_list")


# ----------------------------------
def cargar_servicios(request):
    especialidad_id = request.GET.get("especialidad_id")

    if not especialidad_id:
        return JsonResponse([], safe=False)

    servicios = Servicio.objects.filter(
        especialista_required_id=especialidad_id
    ).values("id", "nombre")

    return JsonResponse(list(servicios), safe=False)


# =====================================================
# REPORTES
# =====================================================
# =====================================================
# REPORTE PDF
# =====================================================


def reporte_veterinarios_pdf(request):

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = 'attachment; filename="veterinarios.pdf"'

    doc = SimpleDocTemplate(response)

    elementos = []

    styles = getSampleStyleSheet()

    titulo = Paragraph("Reporte de Veterinarios", styles["Title"])

    elementos.append(titulo)

    elementos.append(Spacer(1, 20))

    data = [["ID", "Nombre", "Documento", "Especialidad", "Estado"]]

    veterinarios = filtrar_veterinarios(request)

    for p in veterinarios:

        data.append(
            [
                str(p.id),
                str(p.nombre),
                str(p.documento),
                str(p.especialidad),
                str(p.usuario.estado),
            ]
        )

    tabla = Table(data)

    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.green),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ]
        )
    )

    elementos.append(tabla)

    doc.build(elementos)

    return response


# =====================================================
# REPORTE EXCEL
# =====================================================


def reporte_veterinarios_excel(request):

    response = HttpResponse(content_type="application/ms-excel")

    response["Content-Disposition"] = 'attachment; filename="veterinarios.xlsx"'

    workbook = openpyxl.Workbook()

    worksheet = workbook.active

    worksheet.title = "Veterinarios"

    encabezados = ["ID", "Nombre", "Documento", "Especialidad", "Estado"]

    worksheet.append(encabezados)

    veterinarios = filtrar_veterinarios(request)

    for p in veterinarios:

        worksheet.append(
            [
                p.id,
                str(p.nombre),
                str(p.documento),
                str(p.especialidad),
                str(p.usuario.estado),
            ]
        )

    workbook.save(response)

    return response
