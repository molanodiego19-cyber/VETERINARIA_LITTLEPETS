from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
#from citas.models import ConsultaServicio

#class ConsultaServicioListView(ListView):
#    model = ConsultaServicio
#    template_name = 'panel/consultaservicio/list.html'
#    context_object_name = 'consulta_servicios'

#class ConsultaServicioCreateView(CreateView):
#    model = ConsultaServicio
#    fields = '__all__'
#    template_name = 'panel/consultaservicio/form.html'
#    success_url = reverse_lazy('panel:panel_consultaservicio_list')

#class ConsultaServicioUpdateView(UpdateView):
#    model = ConsultaServicio
#    fields = '__all__'
#    template_name = 'panel/consultaservicio/form.html'
#    success_url = reverse_lazy('panel:panel_consultaservicio_list')

#class ConsultaServicioDeleteView(DeleteView):
#    model = ConsultaServicio
#    template_name = 'panel/consultaservicio/delete.html'
#    success_url = reverse_lazy('panel:panel_consultaservicio_list')