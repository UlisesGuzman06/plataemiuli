from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from django.utils import timezone
from .models import Persona, Categoria, Gasto, GastoFijo, Ingreso, PagoSaldo, TipoDivision, Moneda
from .services import get_dolar_rates, calculate_financial_summary

def get_base_context(request):
    """Common context variables for topbar dollar rates and personas."""
    dolar_rates = get_dolar_rates()
    personas = Persona.objects.all()
    categorias = Categoria.objects.all()
    return {
        'dolar_rates': dolar_rates,
        'personas': personas,
        'categorias': categorias,
        'tipos_division': TipoDivision.choices,
        'monedas': Moneda.choices,
    }

def dashboard_view(request):
    context = get_base_context(request)
    summary = calculate_financial_summary()
    recent_gastos = Gasto.objects.select_related('categoria', 'pagado_por')[:10]
    gastos_fijos_proximos = GastoFijo.objects.filter(activo=True).order_by('dia_vencimiento')[:5]
    
    # Calculate monthly category distribution for ARS
    gastos_ars = Gasto.objects.filter(moneda='ARS')
    cat_distribution = {}
    for g in gastos_ars:
        cat_name = g.categoria.nombre if g.categoria else 'Sin Categoría'
        cat_icon = g.categoria.icono if g.categoria else '📦'
        if cat_name not in cat_distribution:
            cat_distribution[cat_name] = {'nombre': cat_name, 'icono': cat_icon, 'monto': Decimal('0.00')}
        cat_distribution[cat_name]['monto'] += g.monto_total

    context.update({
        'summary': summary,
        'recent_gastos': recent_gastos,
        'gastos_fijos_proximos': gastos_fijos_proximos,
        'cat_distribution': list(cat_distribution.values()),
        'active_tab': 'dashboard',
    })
    return render(request, 'finanzas/dashboard.html', context)


def gastos_list_view(request):
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        monto_total = Decimal(request.POST.get('monto_total', '0'))
        moneda = request.POST.get('moneda', 'ARS')
        fecha = request.POST.get('fecha') or timezone.now().date()
        categoria_id = request.POST.get('categoria')
        pagado_por_id = request.POST.get('pagado_por')
        tipo_division = request.POST.get('tipo_division', TipoDivision.EQUITY_50_50)
        
        monto_emi_custom = Decimal(request.POST.get('monto_emi', '0') or '0')
        monto_uli_custom = Decimal(request.POST.get('monto_uli', '0') or '0')
        pct_emi_custom = Decimal(request.POST.get('porcentaje_emi', '50') or '50')
        
        pagado_emi = Decimal(request.POST.get('monto_pagado_emi', '0') or '0')
        pagado_uli = Decimal(request.POST.get('monto_pagado_uli', '0') or '0')
        notas = request.POST.get('notas', '')

        categoria = Categoria.objects.filter(id=categoria_id).first() if categoria_id else None
        pagado_por = get_object_or_404(Persona, id=pagado_por_id)

        gasto = Gasto(
            descripcion=descripcion,
            monto_total=monto_total,
            moneda=moneda,
            fecha=fecha,
            categoria=categoria,
            pagado_por=pagado_por,
            tipo_division=tipo_division,
            porcentaje_emi=pct_emi_custom,
            monto_pagado_emi=pagado_emi,
            monto_pagado_uli=pagado_uli,
            notas=notas
        )

        if tipo_division == TipoDivision.EXACT_AMOUNT:
            gasto.monto_emi = monto_emi_custom
            gasto.monto_uli = monto_uli_custom

        gasto.save()
        messages.success(request, f'Gasto "{descripcion}" cargado correctamente.')
        return redirect('gastos_list')

    context = get_base_context(request)
    gastos = Gasto.objects.select_related('categoria', 'pagado_por').all()

    # Filter logic
    persona_filter = request.GET.get('persona')
    categoria_filter = request.GET.get('categoria')
    moneda_filter = request.GET.get('moneda')

    if persona_filter:
        gastos = gastos.filter(pagado_por__slug=persona_filter)
    if categoria_filter:
        gastos = gastos.filter(categoria_id=categoria_filter)
    if moneda_filter:
        gastos = gastos.filter(moneda=moneda_filter)

    context.update({
        'gastos': gastos,
        'persona_filter': persona_filter,
        'categoria_filter': categoria_filter,
        'moneda_filter': moneda_filter,
        'active_tab': 'gastos',
    })
    return render(request, 'finanzas/gastos.html', context)


def eliminar_gasto_view(request, gasto_id):
    if request.method == 'POST':
        gasto = get_object_or_404(Gasto, id=gasto_id)
        desc = gasto.descripcion
        gasto.delete()
        messages.success(request, f'Gasto "{desc}" eliminado.')
    return redirect('gastos_list')


def gastos_fijos_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        monto_estimado = Decimal(request.POST.get('monto_estimado', '0'))
        moneda = request.POST.get('moneda', 'ARS')
        dia_vencimiento = int(request.POST.get('dia_vencimiento', '10'))
        categoria_id = request.POST.get('categoria')
        responsable = request.POST.get('responsable', 'COMPARTIDO')
        notas = request.POST.get('notas', '')

        categoria = Categoria.objects.filter(id=categoria_id).first() if categoria_id else None

        GastoFijo.objects.create(
            nombre=nombre,
            monto_estimado=monto_estimado,
            moneda=moneda,
            dia_vencimiento=dia_vencimiento,
            categoria=categoria,
            responsable=responsable,
            notas=notas
        )
        messages.success(request, f'Gasto fijo "{nombre}" registrado.')
        return redirect('gastos_fijos')

    context = get_base_context(request)
    gastos_fijos = GastoFijo.objects.select_related('categoria').all()
    context.update({
        'gastos_fijos': gastos_fijos,
        'active_tab': 'gastos_fijos',
    })
    return render(request, 'finanzas/gastos_fijos.html', context)


def toggle_gasto_fijo_view(request, gf_id):
    if request.method == 'POST':
        gf = get_object_or_404(GastoFijo, id=gf_id)
        gf.activo = not gf.activo
        gf.save()
    return redirect('gastos_fijos')


def balance_view(request):
    if request.method == 'POST':
        pagador_id = request.POST.get('pagador')
        receptor_id = request.POST.get('receptor')
        monto = Decimal(request.POST.get('monto', '0'))
        moneda = request.POST.get('moneda', 'ARS')
        fecha = request.POST.get('fecha') or timezone.now().date()
        notas = request.POST.get('notas', '')

        pagador = get_object_or_404(Persona, id=pagador_id)
        receptor = get_object_or_404(Persona, id=receptor_id)

        PagoSaldo.objects.create(
            pagador=pagador,
            receptor=receptor,
            monto=monto,
            moneda=moneda,
            fecha=fecha,
            notas=notas
        )
        messages.success(request, f'Pago de ajuste registrado: {pagador.nombre} ➔ {receptor.nombre} (${monto} {moneda}).')
        return redirect('balance')

    context = get_base_context(request)
    summary = calculate_financial_summary()
    historial_pagos = PagoSaldo.objects.select_related('pagador', 'receptor').all()

    context.update({
        'summary': summary,
        'historial_pagos': historial_pagos,
        'active_tab': 'balance',
    })
    return render(request, 'finanzas/balance.html', context)


def ingresos_view(request):
    if request.method == 'POST':
        persona_id = request.POST.get('persona')
        monto = Decimal(request.POST.get('monto', '0'))
        moneda = request.POST.get('moneda', 'ARS')
        descripcion = request.POST.get('descripcion')
        fecha = request.POST.get('fecha') or timezone.now().date()

        persona = get_object_or_404(Persona, id=persona_id)

        Ingreso.objects.create(
            persona=persona,
            monto=monto,
            moneda=moneda,
            descripcion=descripcion,
            fecha=fecha
        )
        messages.success(request, f'Ingreso de {persona.nombre} por ${monto} {moneda} registrado.')
        return redirect('ingresos')

    context = get_base_context(request)
    ingresos = Ingreso.objects.select_related('persona').all()
    context.update({
        'ingresos': ingresos,
        'active_tab': 'ingresos',
    })
    return render(request, 'finanzas/ingresos.html', context)


def cotizaciones_view(request):
    context = get_base_context(request)
    context.update({
        'active_tab': 'cotizaciones',
    })
    return render(request, 'finanzas/cotizaciones.html', context)
