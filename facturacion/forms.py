from django import forms
from .models import Factura, DetalleFactura

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['metodo_pago', 'notas']

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        exclude = ['total', 'descripcion', 'precio_unitario']  # estos se calculan automáticamente
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'numero_comprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'fechahora_pago': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # Permitir recibir la factura desde la vista
        self.factura = kwargs.pop('factura', None)
        super().__init__(*args, **kwargs)
        if self.factura:
            self.fields['servicio'].queryset = self.factura.cita.servicio.citas.all()  # opcional: filtrar servicios de la cita

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.factura:
            instance.factura = self.factura

        # Llenar precio_unitario y descripcion automáticamente desde el servicio
        if instance.servicio:
            instance.precio_unitario = instance.servicio.precio
            instance.descripcion = instance.servicio.nombre
            instance.total = instance.cantidad * instance.precio_unitario

        if commit:
            instance.save()
        return instance