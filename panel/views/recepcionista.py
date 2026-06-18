from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse

from usuarios.models import Recepcionista
from usuarios.forms import RecepcionistaCompletoForm, RecepcionistaUpdateForm
# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# EXCEL
import openpyxl


def filtrar_recepcionistas(request):

    recepcionistas = (
        Recepcionista.objects.select_related("usuario").all().order_by("-id")
    )

    nombre = request.GET.get("nombre", "").strip()
    documento = request.GET.get("documento", "").strip()
    estado = request.GET.get("estado", "").strip()

    if nombre:
        recepcionistas = recepcionistas.filter(nombre__icontains=nombre)

    if documento:
        recepcionistas = recepcionistas.filter(documento__icontains=documento)

    if estado in ["activo", "inactivo"]:
        recepcionistas = recepcionistas.filter(usuario__estado=estado)

    return recepcionistas


class RecepcionistaListView(ListView):
    model = Recepcionista
    template_name = "panel/recepcionista/list.html"
    context_object_name = "recepcionistas"

    def get_queryset(self):
        return filtrar_recepcionistas(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["estados"] = [
            ("activo", "Activo"),
            ("inactivo", "Inactivo"),
        ]

        return context


class RecepcionistaCreateView(CreateView):
    model = Recepcionista
    form_class = RecepcionistaCompletoForm
    template_name = "panel/recepcionista/form.html"
    success_url = reverse_lazy("panel:panel_recepcionista_list")


class RecepcionistaUpdateView(UpdateView):
    model = Recepcionista
    form_class = RecepcionistaUpdateForm
    template_name = "panel/recepcionista/form.html"
    success_url = reverse_lazy("panel:panel_recepcionista_list")


class RecepcionistaDeleteView(View):
    def post(self, request, pk):
        recepcionista = get_object_or_404(Recepcionista, pk=pk)

        recepcionista.usuario.estado = "inactivo"
        recepcionista.usuario.save()

        return redirect("panel:panel_recepcionista_list")


def reporte_recepcionistas_pdf(request):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="recepcionistas.pdf"'

    doc = SimpleDocTemplate(response)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Reporte de Recepcionistas", styles["Title"]))
    elements.append(Spacer(1, 20))

    data = [["ID", "Nombre", "Documento", "Estado"]]

    recepcionistas = filtrar_recepcionistas(request)

    for r in recepcionistas:
        data.append([str(r.id), str(r.nombre), str(r.documento), str(r.usuario.estado)])

    table = Table(data)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.green),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ]
        )
    )

    elements.append(table)

    doc.build(elements)

    return response


def reporte_recepcionistas_excel(request):

    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = 'attachment; filename="recepcionistas.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Recepcionistas"

    ws.append(["ID", "Nombre", "Documento", "Estado"])

    recepcionistas = filtrar_recepcionistas(request)

    for r in recepcionistas:
        ws.append([r.id, r.nombre, r.documento, r.usuario.estado])

    wb.save(response)

    return response
