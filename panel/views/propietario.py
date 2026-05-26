from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth import get_user_model
from usuarios.models import Propietario
from usuarios.forms import (
    PropietarioCompletoForm,
    PropietarioUpdateForm
)

from django.views import View
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

# =====================================================
# REPORTES
# =====================================================

from django.http import HttpResponse

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

# =====================================================
# FILTRO REUTILIZABLE
# =====================================================

def filtrar_propietarios(request):

    propietarios = Propietario.objects.select_related(
        'usuario'
    ).all().order_by('-id')

    # ==========================================
    # FILTRO NOMBRE
    # ==========================================

    nombre = request.GET.get('nombre')

    if nombre:

        propietarios = propietarios.filter(
            nombre__icontains=nombre
        )

    # ==========================================
    # FILTRO DOCUMENTO
    # ==========================================

    documento = request.GET.get('documento')

    if documento:

        propietarios = propietarios.filter(
            documento__icontains=documento
        )


    # ==========================================
    # FILTRO TELEFONO
    # ==========================================

    telefono = request.GET.get('telefono')

    if telefono:

        propietarios = propietarios.filter(
            telefono__icontains=telefono
        )


    # ==========================================
    # FILTRO CIUDAD
    # ==========================================

    ciudad = request.GET.get('ciudad')

    if ciudad:

        propietarios = propietarios.filter(
            ciudad__icontains=ciudad
        )

    # ==========================================
    # FILTRO ESTADO
    # ==========================================

    estado = request.GET.get('estado')

    if estado:

        propietarios = propietarios.filter(
            usuario__estado=estado
        )

    return propietarios


# =====================================================
# LISTADO
# =====================================================

class PropietarioListView(ListView):

    model = Propietario

    template_name = 'panel/propietario/list.html'

    context_object_name = 'propietarios'

    paginate_by = 10

    # ==========================================
    # QUERYSET
    # ==========================================

    def get_queryset(self):

        return filtrar_propietarios(
            self.request
        )

    # ==========================================
    # CONTEXTO
    # ==========================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['estados'] = [
            ('Activo', 'Activo'),
            ('Inactivo', 'Inactivo')
        ]

        return context


# =====================================================
# CREAR
# =====================================================

class PropietarioCreateView(CreateView):

    model = Propietario

    form_class = PropietarioCompletoForm

    template_name = 'panel/propietario/form.html'

    success_url = reverse_lazy(
        'panel:panel_propietario_list'
    )


# =====================================================
# ACTUALIZAR
# =====================================================

class PropietarioUpdateView(UpdateView):

    model = Propietario

    form_class = PropietarioUpdateForm

    template_name = 'panel/propietario/form.html'

    success_url = reverse_lazy(
        'panel:panel_propietario_list'
    )


# =====================================================
# ELIMINACIÓN LÓGICA
# =====================================================

class PropietarioDeleteView(View):

    def post(self, request, pk):

        propietario = get_object_or_404(
            Propietario,
            pk=pk
        )

        propietario.usuario.estado = 'Inactivo'

        propietario.usuario.save()

        return redirect(
            'panel:panel_propietario_list'
        )


# =====================================================
# REPORTE PDF
# =====================================================

def reporte_propietarios_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="propietarios.pdf"'

    doc = SimpleDocTemplate(response)

    elementos = []

    styles = getSampleStyleSheet()

    titulo = Paragraph(
        "Reporte de Propietarios",
        styles['Title']
    )

    elementos.append(titulo)

    elementos.append(
        Spacer(1, 20)
    )

    data = [[
        'ID',
        'Nombre',
        'Documento',
        'Correo',
        'Ciudad',
        'Teléfono',
        'Estado'
    ]]

    propietarios = filtrar_propietarios(
        request
    )

    for p in propietarios:

        data.append([
            str(p.id),
            str(p.nombre),
            str(p.documento),
            str(p.usuario.correo),
            str(p.ciudad),
            str(p.telefono),
            str(p.usuario.estado)
        ])

    tabla = Table(data)

    tabla.setStyle(TableStyle([

        (
            'BACKGROUND',
            (0, 0),
            (-1, 0),
            colors.green
        ),

        (
            'TEXTCOLOR',
            (0, 0),
            (-1, 0),
            colors.white
        ),

        (
            'GRID',
            (0, 0),
            (-1, -1),
            1,
            colors.black
        ),

        (
            'FONTNAME',
            (0, 0),
            (-1, 0),
            'Helvetica-Bold'
        ),

        (
            'BACKGROUND',
            (0, 1),
            (-1, -1),
            colors.beige
        ),

    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return response


# =====================================================
# REPORTE EXCEL
# =====================================================

def reporte_propietarios_excel(request):

    response = HttpResponse(
        content_type='application/ms-excel'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="propietarios.xlsx"'

    workbook = openpyxl.Workbook()

    worksheet = workbook.active

    worksheet.title = 'Propietarios'

    encabezados = [
        'ID',
        'Nombre',
        'Documento',
        'Correo',
        'Ciudad',
        'Teléfono',
        'Estado'
    ]

    worksheet.append(encabezados)

    propietarios = filtrar_propietarios(
        request
    )

    for p in propietarios:

        worksheet.append([
            p.id,
            str(p.nombre),
            str(p.documento),
            str(p.usuario.correo),
            str(p.ciudad),
            str(p.telefono),
            str(p.usuario.estado)
        ])

    workbook.save(response)

    return response