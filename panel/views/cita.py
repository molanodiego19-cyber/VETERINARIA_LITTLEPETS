from django.views.generic import ListView
from django.http import HttpResponse
from citas.models import Cita, Servicio
from usuarios.models import Veterinario
from usuarios.models import Usuario
# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
# EXCEL
import openpyxl

# =========================================================
# FUNCIÓN REUTILIZABLE PARA FILTRAR CITAS
# =========================================================


def filtrar_citas(request):

    citas = Cita.objects.all().order_by("-fecha", "-hora")

    estado = request.GET.get("estado")
    fecha = request.GET.get("fecha")
    servicio = request.GET.get("servicio")
    veterinario = request.GET.get("veterinario")

    # ==========================================
    # FILTRO ESTADO
    # ==========================================

    if estado:
        citas = citas.filter(estado=estado)

    # ==========================================
    # FILTRO FECHA
    # ==========================================

    if fecha:
        citas = citas.filter(fecha=fecha)

    # ==========================================
    # FILTRO SERVICIO
    # ==========================================

    if servicio:
        citas = citas.filter(servicio_id=servicio)

    # ==========================================
    # FILTRO VETERINARIO
    # ==========================================

    if veterinario:
        citas = citas.filter(veterinario_id=veterinario)

    return citas.order_by("fecha", "hora")


# =========================================================
# LISTADO DE CITAS
# =========================================================
class CitasListView(ListView):

    model = Cita
    context_object_name = "citas"
    ordering = ["-fecha", "-hora"]

    def get_template_names(self):

        usuario_id = self.request.session.get("usuario_id")

        if not usuario_id:
            return ["panel/cita/list.html"]

        try:
            usuario = Usuario.objects.get(id=usuario_id)

            # Recepcionista
            if hasattr(usuario, "recepcionista"):
                return ["panel/cita/list_recepcionista.html"]

        except Usuario.DoesNotExist:
            pass

        # Administrador por defecto
        return ["panel/cita/list.html"]

    def get_queryset(self):
        return filtrar_citas(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["servicios"] = Servicio.objects.all()
        context["veterinarios"] = Veterinario.objects.all()
        context["estados"] = Cita.ESTADOS

        return context


# =========================================================
# REPORTE PDF
# =========================================================


def reporte_citas_pdf(request):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="reporte_citas.pdf"'

    doc = SimpleDocTemplate(response)
    elementos = []
    styles = getSampleStyleSheet()

    # ==========================================
    # OBTENER CITAS
    # ==========================================
    citas = filtrar_citas(request)

    # ==========================================
    # RESUMEN
    # ==========================================
    total_citas = citas.count()

    pendientes = citas.filter(estado="PENDIENTE").count()
    confirmadas = citas.filter(estado="CONFIRMADA").count()
    atendidas = citas.filter(estado="ATENDIDA").count()
    facturadas = citas.filter(estado="FACTURADA").count()
    canceladas = citas.filter(estado="CANCELADA").count()

    # ==========================================
    # TÍTULO
    # ==========================================
    titulo = Paragraph("Reporte General de Citas", styles["Title"])

    elementos.append(titulo)
    elementos.append(Spacer(1, 15))

    # ==========================================
    # RESUMEN ESTADÍSTICO
    # ==========================================
    resumen = f"""
    <b>Total de citas:</b> {total_citas}<br/>
    <b>Pendientes:</b> {pendientes}<br/>
    <b>Confirmadas:</b> {confirmadas}<br/>
    <b>Atendidas:</b> {atendidas}<br/>
    <b>Facturadas:</b> {facturadas}<br/>
    <b>Canceladas:</b> {canceladas}
    """

    elementos.append(Paragraph(resumen, styles["Normal"]))
    elementos.append(Spacer(1, 20))

    # ==========================================
    # TABLA
    # ==========================================
    data = [
        ["ID", "Mascota", "Veterinario", "Servicio", "Fecha", "Hora", "Estado"]
    ]

    for c in citas:
        data.append(
            [
                str(c.id),
                str(c.mascota.nombre),
                str(c.veterinario) if c.veterinario else "Sin asignar",
                str(c.servicio.nombre),
                str(c.fecha),
                str(c.hora),
                str(c.get_estado_display()),
            ]
        )

    tabla = Table(data)

    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.green),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ]
        )
    )

    elementos.append(tabla)

    # ==========================================
    # GENERAR PDF
    # ==========================================
    doc.build(elementos)

    return response


# =========================================================
# REPORTE EXCEL
# =========================================================


def reporte_citas_excel(request):

    response = HttpResponse(content_type="application/ms-excel")

    response["Content-Disposition"] = 'attachment; filename="reporte_citas.xlsx"'

    workbook = openpyxl.Workbook()

    worksheet = workbook.active

    worksheet.title = "Citas"

    # ==========================================
    # ENCABEZADOS
    # ==========================================

    encabezados = [
        "ID",
        "Mascota",
        "Veterinario",
        "Servicio",
        "Fecha",
        "Hora",
        "Estado",
    ]

    worksheet.append(encabezados)

    # ==========================================
    # DATOS
    # ==========================================

    citas = filtrar_citas(request)

    for c in citas:

        worksheet.append(
            [
                c.id,
                str(c.mascota.nombre),
                str(c.veterinario) if c.veterinario else "Sin asignar",
                str(c.servicio.nombre),
                str(c.fecha),
                str(c.hora),
                str(c.get_estado_display()),
            ]
        )

    workbook.save(response)

    return response
