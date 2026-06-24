from django.db import models
from decimal import Decimal
from django.utils import timezone
import uuid


class Factura(models.Model):

    ESTADO_PAGO = [
        ("pendiente", "Pendiente"),
        ("pagada", "Pagada"),
    ]

    estado_pago = models.CharField(
        max_length=15,
        choices=ESTADO_PAGO,
        default="pendiente"
    )

    cita = models.ForeignKey(
        "citas.Cita",
        on_delete=models.CASCADE,
        related_name="facturas"
    )

    numero_factura = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    fecha_emision = models.DateField(auto_now_add=True)

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    impuestos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=[
            ("efectivo", "Efectivo"),
            ("tarjeta", "Tarjeta"),
            ("transferencia", "Transferencia"),
            ("nequi", "Nequi"),
            ("daviplata", "Daviplata"),
        ],
        default="efectivo",
    )

    notas = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    IMPUESTO_PORC = Decimal("0.01")

    def save(self, *args, **kwargs):

        if not self.numero_factura:
            self.numero_factura = (
                f"FAC-{uuid.uuid4().hex[:6].upper()}"
            )

        super().save(*args, **kwargs)

    def crear_desde_cita(self):

        self.save()
        self.generar_detalles()

    def recalcular_totales(self):

        subtotal = sum(
            detalle.total
            for detalle in self.detalles.all()
        )

        self.subtotal = subtotal
        self.impuestos = subtotal * self.IMPUESTO_PORC
        self.total = self.subtotal + self.impuestos

        super().save(
            update_fields=[
                "subtotal",
                "impuestos",
                "total"
            ]
        )

    def generar_detalles(self):

        self.detalles.all().delete()

        # ==========================
        # SERVICIO
        # ==========================

        if self.cita.servicio:

            DetalleFactura.objects.create(
                factura=self,
                servicio=self.cita.servicio,
                descripcion=self.cita.servicio.nombre,
                cantidad=1,
                precio_unitario=self.cita.servicio.precio,
                fechahora_pago=timezone.now(),
            )

        # ==========================
        # VACUNAS
        # ==========================

        for vacunacion in self.cita.vacunaciones.select_related(
            "vacuna"
        ).all():

            DetalleFactura.objects.create(
                factura=self,
                descripcion=f"Vacuna: {vacunacion.vacuna.nombre}",
                cantidad=1,
                precio_unitario=vacunacion.vacuna.precio_venta,
                fechahora_pago=timezone.now(),
            )

        self.recalcular_totales()

    def __str__(self):

        return f"{self.numero_factura}"
    
class DetalleFactura(models.Model):

    factura = models.ForeignKey(
        "Factura",
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    servicio = models.ForeignKey(
        "citas.Servicio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    descripcion = models.CharField(
        max_length=200
    )

    cantidad = models.IntegerField(
        default=1
    )

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    numero_comprobante = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    fechahora_pago = models.DateTimeField(
        blank=True,
        null=True
    )

    notas = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):

        if self.servicio:

            self.descripcion = self.servicio.nombre
            self.precio_unitario = self.servicio.precio

        self.total = self.cantidad * self.precio_unitario

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.descripcion} x "
            f"{self.cantidad} — "
            f"{self.factura.numero_factura}"
        )
    
