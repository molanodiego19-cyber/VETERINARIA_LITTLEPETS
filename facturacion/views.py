from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect

from citas.models import Cita
from .models import Factura
from .forms import FacturaForm

from usuarios.models import Usuario


# =====================================================
# CREAR FACTURA SERVICIO
# =====================================================

def crear_factura_servicio(request, cita_id):

    cita = get_object_or_404(
        Cita.objects.select_related(
            'servicio',
            'mascota',
            'veterinario'
        ),
        id=cita_id
    )

    servicio = cita.servicio

    subtotal = servicio.precio if servicio else Decimal('0.00')

    impuestos = (
        subtotal * Decimal('0.01')
    ).quantize(Decimal('0.01'))

    total = (
        subtotal + impuestos
    ).quantize(Decimal('0.01'))

    # =================================================
    # POST
    # =================================================

    if request.method == "POST":

        form = FacturaForm(request.POST)

        if form.is_valid():

            factura = form.save(commit=False)

            factura.cita = cita
            factura.subtotal = subtotal
            factura.impuestos = impuestos
            factura.total = total

            factura.save()

            # =========================================
            # GENERAR DETALLES
            # =========================================

            factura.generar_detalles()

            # =========================================
            # FINALIZAR CITA
            # =========================================

            cita.estado = 'finalizada'
            cita.save(update_fields=['estado'])

            return redirect(
                'facturacion:detalle_factura',
                factura.id
            )

    # =================================================
    # GET
    # =================================================

    else:

        form = FacturaForm()

    return render(request, 'facturacion/crear_factura.html', {

        'form': form,
        'cita': cita,
        'servicio': servicio,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total

    })


# =====================================================
# DETALLE FACTURA
# =====================================================

def detalle_factura(request, factura_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    factura = get_object_or_404(

        Factura.objects.select_related(
            'cita',
            'cita__mascota',
            'cita__veterinario'
        ),

        id=factura_id
    )

    # =================================================
    # VALIDAR ACCESO
    # =================================================

    if usuario.rol == 'propietario':

        permitido = (
            factura.cita.mascota.propietario.usuario == usuario
        )

        if not permitido:
            return redirect('facturacion:lista_facturas')

    # -------------------------------------------------

    elif usuario.rol == 'veterinario':

        permitido = (
            factura.cita.veterinario.usuario == usuario
        )

        if not permitido:
            return redirect('facturacion:lista_facturas')

    # =================================================
    # DETALLES
    # =================================================

    detalles = factura.detalles.select_related(
        'servicio'
    ).all()

    # =================================================
    # TEMPLATE BASE SEGUN ROL
    # =================================================

    if usuario.rol == 'admin':

        base_template = 'panel/base.html'

    elif usuario.rol == 'veterinario':

        base_template = 'usuarios/base_veterinario.html'

    elif usuario.rol == 'propietario':

        base_template = 'usuarios/base_propietario.html'

    else:

        base_template = 'panel/base.html'

    return render(request, 'panel/detalle_factura/list.html', {

        'factura': factura,
        'detalles': detalles,
        'base_template': base_template

    })


# =====================================================
# LISTA FACTURAS
# =====================================================

def lista_facturas(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    facturas = Factura.objects.select_related(
        'cita',
        'cita__mascota',
        'cita__mascota__propietario',
        'cita__veterinario'
    )

    # =================================================
    # TEMPLATE BASE
    # =================================================

    if usuario.rol == 'admin':

        base_template = 'base.html'

    elif usuario.rol == 'veterinario':

        base_template = 'usuarios/base_veterinario.html'

    elif usuario.rol == 'propietario':

        base_template = 'usuarios/base_propietario.html'

    else:

        base_template = 'panel/base.html'

    # =================================================
    # FILTROS POR ROL
    # =================================================

    if usuario.rol == 'propietario':

        facturas = facturas.filter(
            cita__mascota__propietario__usuario=usuario
        )

    # -------------------------------------------------

    elif usuario.rol == 'veterinario':

        facturas = facturas.filter(
            cita__veterinario__usuario=usuario
        )

    return render(request, 'facturacion/lista_facturas.html', {

        'facturas': facturas.order_by('-fecha_emision'),
        'base_template': base_template

    })

# LISTA FACTURAS VETERINARIO
def lista_facturas_vet(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=usuario_id)

    facturas = Factura.objects.select_related(
        'cita',
        'cita__mascota',
        'cita__veterinario'
    ).filter(
        cita__veterinario__usuario=usuario
    ).order_by('-fecha_emision')

    return render(request, 'facturacion/lista_facturas_vet.html', {

        'facturas': facturas

    })