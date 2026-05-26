from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from citas.models import CategoriaServicios

class CategoriaServicioListView(ListView):
    model = CategoriaServicios
    template_name = 'panel/categoriaservicios/list.html'
    context_object_name = 'categorias'

class CategoriaServicioCreateView(CreateView):
    model = CategoriaServicios
    fields = '__all__'
    template_name = 'panel/categoriaservicios/form.html'
    success_url = reverse_lazy('panel:panel_categoriaservicio_list')

class CategoriaServicioUpdateView(UpdateView):
    model = CategoriaServicios
    fields = '__all__'
    template_name = 'panel/categoriaservicios/form.html'
    success_url = reverse_lazy('panel:panel_categoriaservicio_list')

class CategoriaServicioDeleteView(DeleteView):
    model = CategoriaServicios
    template_name = 'panel/categoriaservicios/delete.html'
    success_url = reverse_lazy('panel:panel_categoriaservicio_list')