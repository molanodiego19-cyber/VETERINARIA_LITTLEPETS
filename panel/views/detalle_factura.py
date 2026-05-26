from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.shortcuts import (
    get_object_or_404,
    redirect
)
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from usuarios.models import Usuario
from facturacion.models import DetalleFactura
from facturacion.forms import DetalleFacturaForm

# LISTADO DETALLES FACTURA
class DetalleFacturaListView(ListView):

    model = DetalleFactura
    template_name = 'panel/detalle_factura/list.html'
    context_object_name = 'detalles'

    # LOGIN
    def dispatch(self, request, *args, **kwargs):

        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')

        return super().dispatch(request, *args, **kwargs)

    # QUERYSET
    def get_queryset(self):

        usuario_id = self.request.session.get('usuario_id')

        if not usuario_id:
            return DetalleFactura.objects.none()

        usuario = Usuario.objects.get(id=usuario_id)

        qs = DetalleFactura.objects.select_related(
            'factura',
            'factura__cita',
            'factura__cita__mascota',
            'factura__cita__mascota__propietario',
            'factura__cita__veterinario',
            'servicio'
        )

        # ADMIN
        if usuario.rol == 'admin':

            self.base_template = 'base.html'

        # PROPIETARIO
        elif usuario.rol == 'propietario':

            self.base_template = 'usuarios/base_propietario.html'

            qs = qs.filter(
                factura__cita__mascota__propietario__usuario=usuario
            )

        # VETERINARIO
        elif usuario.rol == 'veterinario':

            self.base_template = 'usuarios/base_veterinario.html'

            qs = qs.filter(
                factura__cita__veterinario__usuario=usuario
            )

        # OTROS
        else:

            self.base_template = 'usuarios/base.html'

        # FILTROS
        qs = filtrar_detalles(self.request, qs)

        return qs.order_by('-id')

    # CONTEXTO
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['base_template'] = self.base_template

        return context

# CREAR DETALLE FACTURA
class DetalleFacturaCreateView(CreateView):

    model = DetalleFactura
    form_class = DetalleFacturaForm
    template_name = 'panel/detalle_factura/form.html'
    success_url = reverse_lazy('panel:panel_detallefactura_list')

# EDITAR DETALLE FACTURA
class DetalleFacturaUpdateView(UpdateView):

    model = DetalleFactura
    form_class = DetalleFacturaForm
    template_name = 'panel/detalle_factura/form.html'
    success_url = reverse_lazy('panel:panel_detallefactura_list')

# ELIMINAR DETALLE FACTURA
class DetalleFacturaDeleteView(DeleteView):

    model = DetalleFactura
    template_name = 'panel/detalle_factura/delete.html'
    success_url = reverse_lazy('panel:panel_detallefactura_list')

# FILTROS
def filtrar_detalles(request, queryset):

    factura = request.GET.get('factura')
    servicio = request.GET.get('servicio')

    if factura:

        queryset = queryset.filter(
            factura__numero_factura__icontains=factura
        )

    if servicio:

        queryset = queryset.filter(
            servicio__nombre__icontains=servicio
        )

    return queryset

# PDF INDIVIDUAL
def detalle_factura_pdf_view(request, pk):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    detalle = get_object_or_404(
        DetalleFactura.objects.select_related(
            'factura',
            'factura__cita',
            'factura__cita__mascota',
            'factura__cita__veterinario'
        ),
        pk=pk
    )

    # VALIDAR ACCESO
    if usuario.rol == 'propietario':

        permitido = (
            detalle.factura.cita.mascota.propietario.usuario == usuario
        )

        if not permitido:
            return redirect('panel:panel_detallefactura_list')

    elif usuario.rol == 'veterinario':

        permitido = (
            detalle.factura.cita.veterinario.usuario == usuario
        )

        if not permitido:
            return redirect('panel:panel_detallefactura_list')

    template_path = 'panel/detalle_factura/reporte_pdf.html'

    context = {
        'detalle': detalle
    }

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = f'filename="detalle_{detalle.id}.pdf"'

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

# PDF LISTADO
def detalle_factura_pdf_list(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    detalles = DetalleFactura.objects.select_related(
        'factura',
        'factura__cita',
        'factura__cita__mascota',
        'factura__cita__veterinario',
        'servicio'
    )

    # ADMIN
    if usuario.rol == 'admin':

        pass

    # PROPIETARIO
    elif usuario.rol == 'propietario':

        detalles = detalles.filter(
            factura__cita__mascota__propietario__usuario=usuario
        )

    # VETERINARIO
    elif usuario.rol == 'veterinario':

        detalles = detalles.filter(
            factura__cita__veterinario__usuario=usuario
        )

    # FILTROS
    detalles = filtrar_detalles(request, detalles)

    template_path = 'panel/detalle_factura/reporte_pdf.html'

    context = {
        'detalles': detalles
    }

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="detalles_factura.pdf"'

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