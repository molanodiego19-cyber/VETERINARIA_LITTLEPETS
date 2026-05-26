from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView, CreateView, UpdateView, View
from citas.models import Servicio, CategoriaServicios
from veterinarioapp.models import Especialidad
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.shortcuts import render
from facturacion.models import DetalleFactura
from django.db.models import Q

#class ServicioListView(ListView):
#    model = Servicio
#    template_name = 'panel/servicio/list.html'
#    context_object_name = 'servicios'

class ServicioCreateView(CreateView):
    model = Servicio
    fields = '__all__'
    template_name = 'panel/servicio/form.html'
    success_url = reverse_lazy('panel:panel_servicio_list')

class ServicioUpdateView(UpdateView):
    model = Servicio
    fields = '__all__'
    template_name = 'panel/servicio/form.html'
    success_url = reverse_lazy('panel:panel_servicio_list')

class ServicioDeleteView(View):
    def post(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)

        servicio.activo = False
        servicio.save()

        return redirect('panel:panel_servicio_list')
    

class ServicioListView(ListView):
    model = Servicio
    template_name = 'panel/servicio/list.html'
    context_object_name = 'servicios'

    def get_queryset(self):
        queryset = Servicio.objects.select_related(
            'categoria', 'especialista_required'
        ).all()

        # Obtener filtros
        nombre = self.request.GET.get('nombre')
        categoria = self.request.GET.get('categoria')
        especialidad = self.request.GET.get('especialidad')
        precio_min = self.request.GET.get('precio_min')
        precio_max = self.request.GET.get('precio_max')
        activo = self.request.GET.get('activo')

        # Aplicar filtros
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

        if categoria:
            queryset = queryset.filter(categoria_id=categoria)

        if especialidad:
            queryset = queryset.filter(especialista_required_id=especialidad)

        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)

        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)

        # 🔥 ESTE ES EL ERROR MÁS COMÚN
        if activo == "True":
            queryset = queryset.filter(activo=True)
        elif activo == "False":
            queryset = queryset.filter(activo=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaServicios.objects.all()
        context['especialidades'] = Especialidad.objects.all()
        return context
    
def servicio_reporte_pdf(request):
    # Filtrado igual que en el panel
    servicios = Servicio.objects.select_related('categoria', 'especialista_required').all()

    nombre = request.GET.get('nombre')
    categoria = request.GET.get('categoria')
    especialidad = request.GET.get('especialidad')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    activo = request.GET.get('activo')

    if nombre:
        servicios = servicios.filter(nombre__icontains=nombre)
    if categoria:
        servicios = servicios.filter(categoria_id=categoria)
    if especialidad:
        servicios = servicios.filter(especialista_required_id=especialidad)
    if precio_min:
        servicios = servicios.filter(precio__gte=precio_min)
    if precio_max:
        servicios = servicios.filter(precio__lte=precio_max)
    if activo == "True":
        servicios = servicios.filter(activo=True)
    elif activo == "False":
        servicios = servicios.filter(activo=False)

    context = {
        'servicios': servicios
    }

    # Cargar template
    template = get_template('panel/servicio/reporte_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Reporte_Servicios.pdf"'

    # Generar PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generando PDF: %s" % pisa_status.err)
    return response

def historial_servicio(request):

    servicios = (
        DetalleFactura.objects
        .select_related(
            'servicio',
            'factura',
            'factura__cita',
        )
        .filter(
            Q(factura__cita__estado='finalizada')
        )
        .values(
            'servicio__id',
            'servicio__nombre'
        )
        .annotate(
            total_cantidad=Count('id'),
            total_ingresos=Sum('total')
        )
        .order_by('-total_cantidad')
    )

    return render(
        request,
        'panel/servicio/servicios_finalizados.html',
        {'servicios': servicios}
    )