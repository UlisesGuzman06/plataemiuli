from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from decimal import Decimal
from django.utils import timezone
from .models import Persona, Gasto, GastoFijo, TipoDivision
from .services import get_dolar_rates, calculate_financial_summary

MESES_NOMBRES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
    7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

def get_base_context(request):
    """Common context variables for topbar dollar rates."""
    dolar_rates = get_dolar_rates()
    return {
        'dolar_rates': dolar_rates,
        'tipos_division': TipoDivision.choices,
    }

def dashboard_view(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        monto_total = Decimal(request.POST.get('monto_total', '0'))
        fecha = request.POST.get('fecha') or timezone.now().date()
        tipo_division = request.POST.get('tipo_division', TipoDivision.EQUITY_50_50)
        
        monto_emi_custom = Decimal(request.POST.get('monto_emi', '0') or '0')
        monto_uli_custom = Decimal(request.POST.get('monto_uli', '0') or '0')
        pct_emi_custom = Decimal(request.POST.get('porcentaje_emi', '50') or '50')
        notas = request.POST.get('notas', '')

        gasto = Gasto(
            descripcion=descripcion,
            monto_total=monto_total,
            fecha=fecha,
            tipo_division=tipo_division,
            porcentaje_emi=pct_emi_custom,
            notas=notas
        )

        if tipo_division == TipoDivision.EXACT_AMOUNT:
            gasto.monto_emi = monto_emi_custom
            gasto.monto_uli = monto_uli_custom

        gasto.save()
        messages.success(request, f'Gasto "{descripcion}" cargado correctamente.')
        return redirect('dashboard')

    context = get_base_context(request)
    now = timezone.now().date()
    year = now.year
    month = now.month
    
    summary = calculate_financial_summary(year=year, month=month)
    
    gastos_qs = Gasto.objects.filter(fecha__year=year, fecha__month=month)
    paginator = Paginator(gastos_qs, 10)
    page_number = request.GET.get('page')
    gastos_page = paginator.get_page(page_number)

    gastos_fijos_proximos = GastoFijo.objects.filter(activo=True).order_by('dia_vencimiento')[:10]
    
    context.update({
        'summary': summary,
        'gastos': gastos_page,
        'gastos_fijos_proximos': gastos_fijos_proximos,
        'mes_actual_nombre': MESES_NOMBRES.get(month, ''),
        'anio_actual': year,
        'active_tab': 'dashboard',
    })
    return render(request, 'finanzas/dashboard.html', context)


def editar_gasto_view(request, gasto_id):
    gasto = get_object_or_404(Gasto, id=gasto_id)
    if request.method == 'POST':
        gasto.descripcion = request.POST.get('descripcion')
        gasto.monto_total = Decimal(request.POST.get('monto_total', '0'))
        gasto.fecha = request.POST.get('fecha') or gasto.fecha
        gasto.tipo_division = request.POST.get('tipo_division', gasto.tipo_division)
        gasto.notas = request.POST.get('notas', '')

        if gasto.tipo_division == TipoDivision.EXACT_AMOUNT:
            gasto.monto_emi = Decimal(request.POST.get('monto_emi', '0') or '0')
            gasto.monto_uli = Decimal(request.POST.get('monto_uli', '0') or '0')

        gasto.save()
        messages.success(request, f'Gasto "{gasto.descripcion}" actualizado correctamente.')
        return redirect('dashboard')

    return redirect('dashboard')


def eliminar_gasto_view(request, gasto_id):
    if request.method == 'POST':
        gasto = get_object_or_404(Gasto, id=gasto_id)
        desc = gasto.descripcion
        gasto.delete()
        messages.success(request, f'Gasto "{desc}" eliminado.')
    return redirect('dashboard')


def gastos_fijos_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        monto_estimado = Decimal(request.POST.get('monto_estimado', '0'))
        dia_vencimiento = int(request.POST.get('dia_vencimiento', '1'))
        responsable = request.POST.get('responsable', 'COMPARTIDO')
        
        es_cuota = request.POST.get('es_cuota') == 'on'
        cuotas_totales = request.POST.get('cuotas_totales')
        cuotas_restantes = request.POST.get('cuotas_restantes')
        fecha_fin_cuota = request.POST.get('fecha_fin_cuota') or None

        c_tot = int(cuotas_totales) if (es_cuota and cuotas_totales) else None
        c_rest = int(cuotas_restantes) if (es_cuota and cuotas_restantes) else None

        GastoFijo.objects.create(
            nombre=nombre,
            monto_estimado=monto_estimado,
            dia_vencimiento=dia_vencimiento,
            responsable=responsable,
            es_cuota=es_cuota,
            cuotas_totales=c_tot,
            cuotas_restantes=c_rest,
            fecha_fin_cuota=fecha_fin_cuota if es_cuota else None,
            activo=True
        )
        messages.success(request, f'Gasto fijo "{nombre}" registrado.')
        return redirect('gastos_fijos')

    context = get_base_context(request)
    gastos_fijos = GastoFijo.objects.all()
    context.update({
        'gastos_fijos': gastos_fijos,
        'active_tab': 'gastos_fijos',
    })
    return render(request, 'finanzas/gastos_fijos.html', context)


def editar_gasto_fijo_view(request, gf_id):
    gf = get_object_or_404(GastoFijo, id=gf_id)
    if request.method == 'POST':
        gf.nombre = request.POST.get('nombre')
        gf.monto_estimado = Decimal(request.POST.get('monto_estimado', '0'))
        gf.dia_vencimiento = int(request.POST.get('dia_vencimiento', '1'))
        gf.responsable = request.POST.get('responsable', gf.responsable)
        
        gf.es_cuota = request.POST.get('es_cuota') == 'on'
        c_tot = request.POST.get('cuotas_totales')
        c_rest = request.POST.get('cuotas_restantes')
        gf.fecha_fin_cuota = request.POST.get('fecha_fin_cuota') or None

        gf.cuotas_totales = int(c_tot) if (gf.es_cuota and c_tot) else None
        gf.cuotas_restantes = int(c_rest) if (gf.es_cuota and c_rest) else None

        gf.save()
        messages.success(request, f'Gasto fijo "{gf.nombre}" actualizado correctamente.')
        return redirect('gastos_fijos')

    return redirect('gastos_fijos')


def descontar_cuota_view(request, gf_id):
    if request.method == 'POST':
        gf = get_object_or_404(GastoFijo, id=gf_id)
        gf.descollar_cuota()
        if gf.cuotas_restantes == 0:
            messages.success(request, f'¡Gasto fijo "{gf.nombre}" completó todas sus cuotas y se finalizó! 🎉')
        else:
            messages.success(request, f'Se descontó 1 cuota de "{gf.nombre}". Quedan {gf.cuotas_restantes} cuotas.')
    return redirect('gastos_fijos')


def toggle_gasto_fijo_view(request, gf_id):
    if request.method == 'POST':
        gf = get_object_or_404(GastoFijo, id=gf_id)
        gf.activo = not gf.activo
        gf.save()
    return redirect('gastos_fijos')


def eliminar_gasto_fijo_view(request, gf_id):
    if request.method == 'POST':
        gf = get_object_or_404(GastoFijo, id=gf_id)
        nombre = gf.nombre
        gf.delete()
        messages.success(request, f'Gasto fijo "{nombre}" eliminado de la base de datos.')
    return redirect('gastos_fijos')


def cotizaciones_view(request):
    context = get_base_context(request)
    context.update({
        'active_tab': 'cotizaciones',
    })
    return render(request, 'finanzas/cotizaciones.html', context)
