from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from mascota.models import Mascota
from citas.models import Cita, Servicio
from usuarios.models import Propietario
from facturacion.models import Factura
from decimal import Decimal

# =========================================================
# VALIDACIÓN MANUAL DE SESIÓN
# =========================================================

def verificar_sesion(request):
    return request.session.get('usuario_id')

def verificar_rol(request, rol_permitido):
    return request.session.get('rol') == rol_permitido

# =========================================================
# DASHBOARD ADMINISTRADOR
# =========================================================

def dashboard(request):
    if not verificar_sesion(request):
        return redirect('login')
        
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    hace_30_dias = hoy - timedelta(days=30)

    # Contadores Globales / Históricos (Para las tarjetas superiores del HTML)
    total_mascotas = Mascota.objects.count()
    total_citas = Cita.objects.count()
    total_finalizadas = Cita.objects.filter(estado='Finalizada').count()
    total_pendientes = Cita.objects.filter(estado='Pendiente').count()

    # =====================================================
    # CITAS DEL DÍA (Estadísticas operacionales internas)
    # =====================================================
    citas_hoy_stats = Cita.objects.filter(
    fecha=hoy
).aggregate(

    agendadas=Count('id'),

    activas=Count(
        'id',
        filter=~Q(estado='cancelada')
    ),

    pendientes=Count(
        'id',
        filter=Q(estado='pendiente')
    ),

    canceladas=Count(
        'id',
        filter=Q(estado='cancelada')
    ),

    finalizadas=Count(
        'id',
        filter=Q(estado='finalizada')
    )
)

    # =====================================================
    # INGRESOS
    # =====================================================
    ingresos_dia = Factura.objects.filter(fecha_creacion__gte=hoy).aggregate(total=Sum('total'))['total']

    if ingresos_dia is None:
        ingresos_dia = Decimal('0.00')    
    ingresos_mes = Factura.objects.filter(fecha_creacion__gte=inicio_mes).aggregate(total=Sum('total'))['total'] or 0

    print("INGRESOS DIA:", ingresos_dia)
    print(type(ingresos_dia))
    # =====================================================
    # SERVICIOS POPULARES
    # =====================================================
    servicios_populares = Servicio.objects.annotate(
        cuanto=Count('citas') # Asegúrate que el related_name en tu modelo Cita sea 'citas'
    ).order_by('-cuanto')[:5]

    # =====================================================
    # TASA NO SHOW
    # =====================================================
    total_historico = Cita.objects.exclude(estado='pendiente').count()
    inasistencias = Cita.objects.filter(estado='cancelada').count()
    tasa_no_show = ((inasistencias / total_historico) * 100) if total_historico > 0 else 0

    # =====================================================
    # CLIENTES NUEVOS
    # =====================================================
    nuevos_clientes = Propietario.objects.filter(fecha_registro__gte=hace_30_dias).count()

    # Data de Tablas requerida por tu HTML
    ultimas_mascotas = Mascota.objects.order_by('-id')[:5]
    citas_finalizadas = Cita.objects.filter(estado='finalizada').order_by('-fecha', '-hora')[:5]

    context = {
        # Globales para tarjetas
        'total_mascotas': total_mascotas,
        'total_citas': total_citas,
        'total_finalizadas': total_finalizadas,
        'total_pendientes': total_pendientes,
        
        # Métricas de negocio avanzadas
        'citas_stats': citas_hoy_stats,
        'ingresos_dia': ingresos_dia,
        'ingresos_mes': ingresos_mes,
        'tasa_no_show': round(tasa_no_show, 1),
        'nuevos_clientes': nuevos_clientes,
        
        # Listados para las tablas
        'ultimas_mascotas': ultimas_mascotas,
        'citas_finalizadas': citas_finalizadas,
        'servicios_populares': servicios_populares,
    }

    return render(request, 'panel/dashboard.html', context)


# =========================================================
# PERFIL PROPIETARIO
# =========================================================

def perfil_propietario(request):
    if not verificar_sesion(request):
        return redirect('login')

    if not verificar_rol(request, 'Propietario'):
        return redirect('sin_permiso')

    usuario_id = request.session.get('usuario_id')
    propietario = Propietario.objects.get(id=usuario_id)
    mascotas = Mascota.objects.filter(propietario=propietario)

    total_mascotas = mascotas.count()
    total_citas = Cita.objects.filter(mascota__propietario=propietario).count()
    
    # Adaptado a las variables que exige el HTML unificado
    proximas_citas = Cita.objects.filter(
        mascota__propietario=propietario,
        fecha__gte=timezone.now().date()
    ).order_by('fecha', 'hora')[:5]

    context = {
        'total_mascotas': total_mascotas,
        'total_citas': total_citas,
        'citas_finalizadas': proximas_citas, # Cambiado para que use la tabla del HTML común
        'mascotas': mascotas,
    }

    return render(request, 'panel/dashboard.html', context)


# =========================================================
# PERFIL VETERINARIO
# =========================================================

def perfil_veterinario(request):
    if not verificar_sesion(request):
        return redirect('login')

    if not verificar_rol(request, 'Veterinario'):
        return redirect('sin_permiso')

    usuario_id = request.session.get('usuario_id')
    hoy = timezone.now().date()

    citas_hoy = Cita.objects.filter(veterinario_id=usuario_id, fecha=hoy)

    context = {
        'total_citas': citas_hoy.count(),
        'total_pendientes': citas_hoy.filter(estado='Pendiente').count(),
        'total_finalizadas': citas_hoy.filter(estado='Finalizada').count(),
        'citas_finalizadas': citas_hoy.order_by('hora'), # Mapeado al loop de la tabla
    }

    return render(request, 'panel/dashboard.html', context)

# NOTA: Debes aplicar esta misma homologación de variables de contexto 
# para perfil_estilista y perfil_recepcionista si van a apuntar al mismo template.

