from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from citas.models import Cita, Servicio
from usuarios.models import Usuario
from django.utils import timezone
from .models import Factura
from .forms import FacturaForm


def crear_factura_servicio(request, cita_id):

    # ==========================================
    # VALIDAR SESIÓN
    # ==========================================

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if usuario.rol not in ["recepcionista", "admin"]:
        messages.error(request, "No tiene permisos para facturar.")
        return redirect("usuarios:login")

    # ==========================================
    # OBTENER CITA
    # ==========================================

    cita = get_object_or_404(
        Cita.objects.select_related(
            "servicio", "servicio_realizado", "mascota", "veterinario"
        ),
        id=cita_id,
    )

    # ==========================================
    # VALIDAR ESTADO
    # ==========================================

    if cita.estado != "atendida":

        messages.error(request, "La cita debe estar atendida antes de facturar.")

        return redirect("panel:panel_cita_list")

    # ==========================================
    # EVITAR FACTURAS DUPLICADAS
    # ==========================================

    factura_existente = Factura.objects.filter(cita=cita).first()

    if factura_existente:

        messages.warning(request, "Esta cita ya fue facturada.")

        return redirect("facturacion:detalle_factura", factura_existente.id)

    # ==========================================
    # SERVICIO A FACTURAR
    # ==========================================

    servicio = cita.servicio_realizado if cita.servicio_realizado else cita.servicio

    subtotal = servicio.precio if servicio else Decimal("0.00")

    impuestos = (subtotal * Decimal("0.01")).quantize(Decimal("0.01"))

    total = (subtotal + impuestos).quantize(Decimal("0.01"))

    # ==========================================
    # GUARDAR FACTURA
    # ==========================================

    if request.method == "POST":

        form = FacturaForm(request.POST)

        if form.is_valid():

            factura = form.save(commit=False)

            factura.cita = cita

            # ======================================
            # TRAZABILIDAD DE CAMBIO
            # ======================================

            hubo_cambio = (
                cita.servicio_realizado and cita.servicio_realizado != cita.servicio
            )

            if hubo_cambio:

                factura.servicio_original = cita.servicio

                factura.servicio_cambiado = cita.servicio_realizado

                factura.motivo_cambio = cita.motivo_cambio_servicio

                subtotal = cita.servicio_realizado.precio

            else:

                subtotal = cita.servicio.precio if cita.servicio else Decimal("0.00")

            # ======================================
            # TOTALES
            # ======================================

            factura.subtotal = subtotal

            factura.impuestos = (subtotal * Decimal("0.01")).quantize(Decimal("0.01"))

            factura.total = (factura.subtotal + factura.impuestos).quantize(
                Decimal("0.01")
            )

            factura.save()

            # ======================================
            # DETALLES
            # ======================================

            factura.generar_detalles()

            detalle = factura.detalles.first()

            if detalle and hubo_cambio:

                detalle.servicio = cita.servicio

                detalle.servicio_cambiado = cita.servicio_realizado

                detalle.notas = (
                    f"Servicio cambiado por veterinario. "
                    f"Motivo: "
                    f"{cita.motivo_cambio_servicio}"
                )

                detalle.save()

            # ======================================
            # ACTUALIZAR CITA
            # ======================================

            cita.estado = "facturada"

            cita.save(update_fields=["estado"])

            messages.success(request, "Factura creada correctamente.")

            return redirect("facturacion:detalle_factura", factura.id)

    else:

        form = FacturaForm()

    # ==========================================
    # RENDER
    # ==========================================

    return render(
        request,
        "facturacion/crear_factura.html",
        {
            "form": form,
            "cita": cita,
            "servicio": servicio,
            "subtotal": subtotal,
            "impuestos": impuestos,
            "total": total,
            "servicios": Servicio.objects.filter(activo=True),
        },
    )


def cambiar_servicio_factura(request, factura_id):

    factura = get_object_or_404(Factura, id=factura_id)

    detalle = factura.detalles.first()

    if request.method == "POST":

        servicio_id = request.POST.get("servicio_cambiado")

        motivo = request.POST.get("motivo_cambio")

        if servicio_id:

            nuevo_servicio = Servicio.objects.get(id=servicio_id)

            factura.servicio_cambiado = nuevo_servicio
            factura.motivo_cambio = motivo
            factura.fecha_cambio = timezone.now()

            factura.save()

            detalle.servicio_cambiado = nuevo_servicio
            detalle.notas = motivo
            detalle.save()

            messages.success(request, "Servicio actualizado correctamente.")

            return redirect("facturacion:detalle_factura", factura.id)

    servicios = Servicio.objects.filter(estado="activo")

    return render(
        request,
        "facturacion/cambiar_servicio.html",
        {"factura": factura, "servicios": servicios},
    )


# =====================================================
# DETALLE FACTURA
# =====================================================


def detalle_factura(request, factura_id):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=usuario_id)

    factura = get_object_or_404(
        Factura.objects.select_related("cita", "cita__mascota", "cita__veterinario"),
        id=factura_id,
    )

    # =================================================
    # VALIDAR ACCESO
    # =================================================

    if usuario.rol == "propietario":

        permitido = factura.cita.mascota.propietario.usuario == usuario

        if not permitido:
            return redirect("facturacion:lista_facturas")

    # -------------------------------------------------

    elif usuario.rol == "veterinario":
        return redirect("usuarios:login")

    # =================================================
    # DETALLES
    # =================================================

    detalles = factura.detalles.select_related(
        "factura", "servicio", "servicio_cambiado"
    ).all()

    # =================================================
    # TEMPLATE BASE SEGUN ROL
    # =================================================

    if usuario.rol == "admin":

        base_template = "panel/base.html"

    elif usuario.rol == "propietario":

        base_template = "usuarios/base_propietario.html"

    else:

        base_template = "usuarios/base_recepcionista.html"

    return render(
        request,
        "panel/detalle_factura/list.html",
        {"factura": factura, "detalles": detalles, "base_template": base_template},
    )


# =====================================================
# LISTA FACTURAS
# =====================================================


def lista_facturas(request):

    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return redirect("usuarios:login")

    usuario = Usuario.objects.get(id=usuario_id)

    facturas = Factura.objects.select_related(
        "cita", "cita__mascota", "cita__mascota__propietario", "cita__veterinario"
    )

    # =================================================
    # TEMPLATE BASE
    # =================================================

    if usuario.rol == "admin":

        base_template = "base.html"

    elif usuario.rol == "propietario":

        base_template = "usuarios/base_propietario.html"

    else:

        base_template = "panel/base.html"

    # =================================================
    # FILTROS POR ROL
    # =================================================

    if usuario.rol == "propietario":

        facturas = facturas.filter(cita__mascota__propietario__usuario=usuario)

    return render(
        request,
        "facturacion/lista_facturas.html",
        {
            "facturas": facturas.order_by("-fecha_emision"),
            "base_template": base_template,
        },
    )


def facturas_pendientes(request):

    citas_pendientes = Cita.objects.filter(estado="atendida").select_related(
        "mascota", "dueño", "servicio"
    )

    return render(
        request,
        "facturacion/facturas_pendientes.html",
        {"citas_pendientes": citas_pendientes},
    )


def cobrar_factura(request, factura_id):

    factura = get_object_or_404(
        Factura.objects.select_related(
            "cita", "cita__mascota", "cita__veterinario", "cita__servicio"
        ),
        id=factura_id,
    )

    if request.method == "POST":

        factura.metodo_pago = request.POST.get("metodo_pago")

        factura.notas = request.POST.get("notas")

        factura.estado_pago = "pagada"

        factura.save()

        messages.success(request, "Factura cobrada correctamente.")

        return redirect("facturacion:detalle_factura", factura.id)

    return render(request, "facturacion/cobrar_factura.html", {"factura": factura})
