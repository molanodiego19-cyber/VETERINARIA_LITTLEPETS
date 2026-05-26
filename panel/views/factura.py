# views.py

from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import redirect

from xhtml2pdf import pisa

from usuarios.models import Usuario
from facturacion.models import Factura
from facturacion.forms import FacturaForm

# LISTADO FACTURAS
class FacturaListView(ListView):

    model = Factura
    template_name = 'panel/facturas/list.html'
    context_object_name = 'facturas'

    def dispatch(self, request, *args, **kwargs):

        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')

        return super().dispatch(request, *args, **kwargs)

    # QUERYSET
    def get_queryset(self):

        usuario_id = self.request.session.get('usuario_id')

        if not usuario_id:
            return Factura.objects.none()

        usuario = Usuario.objects.get(id=usuario_id)

        qs = Factura.objects.select_related(
            'cita',
            'cita__mascota',
            'cita__mascota__propietario',
            'cita__veterinario'
        )

        # ADMIN
        if usuario.rol == 'admin':

            self.base_template = 'base.html'

        # PROPIETARIO
        elif usuario.rol == 'propietario':

            self.base_template = 'propietario/base_propietario.html'

            qs = qs.filter(
                cita__mascota__propietario__usuario=usuario
            )

        # VETERINARIO
        elif usuario.rol == 'veterinario':

            self.base_template = 'usuarios/base_veterinario.html'

            qs = qs.filter(
                cita__veterinario__usuario=usuario
            )

        # OTROS
        else:

            self.base_template = 'usuarios/base.html'

        qs = qs.order_by('-fecha_emision')

        return self.filtrar_facturas(qs)

    # CONTEXTO
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['base_template'] = self.base_template

        return context

    # FILTROS
    def filtrar_facturas(self, queryset):

        numero_factura = self.request.GET.get('numero_factura')
        dueño = self.request.GET.get('dueño')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        metodo_pago = self.request.GET.get('metodo_pago')

        if numero_factura:

            queryset = queryset.filter(
                numero_factura__icontains=numero_factura
            )

        if dueño:

            queryset = queryset.filter(
                cita__mascota__propietario__nombre__icontains=dueño
            )

        if fecha_desde:

            queryset = queryset.filter(
                fecha_emision__gte=fecha_desde
            )

        if fecha_hasta:

            queryset = queryset.filter(
                fecha_emision__lte=fecha_hasta
            )

        if metodo_pago:

            queryset = queryset.filter(
                metodo_pago=metodo_pago
            )

        return queryset

# CREAR FACTURA
class FacturaCreateView(CreateView):

    model = Factura
    form_class = FacturaForm
    template_name = 'panel/facturas/form.html'
    success_url = reverse_lazy('panel:panel_factura_list')

# EDITAR FACTURA
class FacturaUpdateView(UpdateView):

    model = Factura
    form_class = FacturaForm
    template_name = 'panel/facturas/form.html'
    success_url = reverse_lazy('panel:panel_factura_list')

# ELIMINAR FACTURA
class FacturaDeleteView(DeleteView):

    model = Factura
    template_name = 'panel/facturas/delete.html'
    success_url = reverse_lazy('panel:panel_factura_list')

# PDF FACTURA INDIVIDUAL
def factura_pdf_view(request, pk):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    factura = Factura.objects.select_related(
        'cita',
        'cita__mascota',
        'cita__veterinario'
    ).get(pk=pk)

    # VALIDAR ACCESO
    if usuario.rol == 'propietario':

        permitido = (
            factura.cita.mascota.propietario.usuario == usuario
        )

        if not permitido:
            return redirect('panel:panel_factura_list')

    elif usuario.rol == 'veterinario':

        permitido = (
            factura.cita.veterinario.usuario == usuario
        )

        if not permitido:
            return redirect('panel:panel_factura_list')

    template_path = 'panel/facturas/reporte_pdf.html'

    context = {
        'factura': factura
    }

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = f'filename="factura_{factura.id}.pdf"'

    template = get_template(template_path)

    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html,
        dest=response
    )

    if pisa_status.err:

        return HttpResponse(
            'Error al generar PDF: <pre>' + html + '</pre>'
        )

    return response

# PDF LISTADO FACTURAS
def factura_pdf_list(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    facturas = Factura.objects.select_related(
        'cita',
        'cita__mascota',
        'cita__veterinario'
    )

    # ADMIN
    if usuario.rol == 'admin':

        pass

    # PROPIETARIO
    elif usuario.rol == 'propietario':

        facturas = facturas.filter(
            cita__mascota__propietario__usuario=usuario
        )

    # VETERINARIO
    elif usuario.rol == 'veterinario':

        facturas = facturas.filter(
            cita__veterinario__usuario=usuario
        )

    # FILTROS
    facturas = filtrar_facturas(request, facturas)

    template_path = 'panel/facturas/reporte_pdf.html'

    context = {
        'facturas': facturas
    }

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="facturas.pdf"'

    template = get_template(template_path)

    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html,
        dest=response
    )

    if pisa_status.err:

        return HttpResponse(
            'Error al generar PDF <pre>' + html + '</pre>'
        )

    return response

# FILTROS GENERALES
def filtrar_facturas(request, queryset):

    numero_factura = request.GET.get('numero_factura')
    dueño = request.GET.get('dueño')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    metodo_pago = request.GET.get('metodo_pago')

    if numero_factura:

        queryset = queryset.filter(
            numero_factura__icontains=numero_factura
        )

    if dueño:

        queryset = queryset.filter(
            cita__mascota__propietario__nombre__icontains=dueño
        )

    if fecha_desde:

        queryset = queryset.filter(
            fecha_emision__gte=fecha_desde
        )

    if fecha_hasta:

        queryset = queryset.filter(
            fecha_emision__lte=fecha_hasta
        )

    if metodo_pago:

        queryset = queryset.filter(
            metodo_pago=metodo_pago
        )

    return queryset