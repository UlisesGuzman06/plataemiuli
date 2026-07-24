import requests
from decimal import Decimal
from django.db.models import Sum
from .models import Persona, Gasto, PagoSaldo, GastoFijo, Ingreso, TipoDivision

DOLAR_API_URL = "https://dolarapi.com/v1/dolares"

_rates_cache = None
_rates_timestamp = 0

def get_dolar_rates():
    """Fetch live dollar rates from DolarApi.com with graceful fallback."""
    global _rates_cache, _rates_timestamp
    import time
    now = time.time()
    if _rates_cache and (now - _rates_timestamp < 300): # 5 min cache
        return _rates_cache

    try:
        resp = requests.get(DOLAR_API_URL, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            rates = {}
            for item in data:
                casa = item.get('casa', '').lower()
                rates[casa] = {
                    'nombre': item.get('nombre'),
                    'compra': item.get('compra'),
                    'venta': item.get('venta'),
                    'fecha': item.get('fechaActualizacion'),
                }
            _rates_cache = rates
            _rates_timestamp = now
            return rates
    except Exception as e:
        print(f"Error fetching DolarApi rates: {e}")

    # Fallback default values
    return {
        'blue': {'nombre': 'Dólar Blue', 'compra': 1380.0, 'venta': 1400.0},
        'bolsa': {'nombre': 'Dólar MEP', 'compra': 1360.0, 'venta': 1375.0},
        'oficial': {'nombre': 'Dólar Oficial', 'compra': 940.0, 'venta': 980.0},
    }


def calculate_financial_summary():
    """
    Core mathematical engine for Plata Emi y Uli.
    Calculates exact debt balances, monthly totals, income vs expense, and fixed costs.
    """
    personas = {p.slug: p for p in Persona.objects.all()}
    emi = personas.get('emi')
    uli = personas.get('uli')

    summary = {
        'ars': {
            'emi_paid': Decimal('0.00'),
            'emi_owed_share': Decimal('0.00'),
            'uli_paid': Decimal('0.00'),
            'uli_owed_share': Decimal('0.00'),
            'net_balance': Decimal('0.00'), # Positive = Uli owes Emi, Negative = Emi owes Uli
            'total_gastos': Decimal('0.00'),
            'total_ingresos_emi': Decimal('0.00'),
            'total_ingresos_uli': Decimal('0.00'),
        },
        'usd': {
            'emi_paid': Decimal('0.00'),
            'emi_owed_share': Decimal('0.00'),
            'uli_paid': Decimal('0.00'),
            'uli_owed_share': Decimal('0.00'),
            'net_balance': Decimal('0.00'),
            'total_gastos': Decimal('0.00'),
            'total_ingresos_emi': Decimal('0.00'),
            'total_ingresos_uli': Decimal('0.00'),
        },
        'deuda_texto': {'ars': 'Están al día', 'usd': 'Están al día'},
        'quien_debe': {'ars': None, 'usd': None}, # 'emi' or 'uli' or None
        'monto_deuda': {'ars': Decimal('0.00'), 'usd': Decimal('0.00')},
    }

    if not emi or not uli:
        return summary

    for moneda in ['ARS', 'USD']:
        m_key = moneda.lower()

        # Gastos procesados
        gastos = Gasto.objects.filter(moneda=moneda)
        for g in gastos:
            if g.tipo_division != TipoDivision.PERSONAL:
                summary[m_key]['total_gastos'] += g.monto_total
                summary[m_key]['emi_paid'] += g.monto_pagado_emi
                summary[m_key]['uli_paid'] += g.monto_pagado_uli
                summary[m_key]['emi_owed_share'] += g.monto_emi
                summary[m_key]['uli_owed_share'] += g.monto_uli

        # Liquidaciones (PagoSaldo)
        pagos = PagoSaldo.objects.filter(moneda=moneda)
        pagos_emi_a_uli = sum([p.monto for p in pagos if p.pagador == emi and p.receptor == uli], Decimal('0.00'))
        pagos_uli_a_emi = sum([p.monto for p in pagos if p.pagador == uli and p.receptor == emi], Decimal('0.00'))

        # Net balance for Emi: (What Emi paid - What Emi should pay) + (Settlement Emi gave - Settlement Emi got)
        emi_net = (summary[m_key]['emi_paid'] - summary[m_key]['emi_owed_share']) + (pagos_emi_a_uli - pagos_uli_a_emi)
        summary[m_key]['net_balance'] = emi_net

        if emi_net > Decimal('0.01'):
            summary[m_key]['quien_debe'] = 'uli'
            summary[m_key]['monto_deuda'] = round(emi_net, 2)
            summary[m_key]['deuda_texto'] = f"Uli le debe a Emi"
        elif emi_net < Decimal('-0.01'):
            summary[m_key]['quien_debe'] = 'emi'
            summary[m_key]['monto_deuda'] = round(abs(emi_net), 2)
            summary[m_key]['deuda_texto'] = f"Emi le debe a Uli"
        else:
            summary[m_key]['deuda_texto'] = "¡Están al día! 👏"

        # Ingresos
        ingresos_emi = Ingreso.objects.filter(persona=emi, moneda=moneda).aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        ingresos_uli = Ingreso.objects.filter(persona=uli, moneda=moneda).aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        summary[m_key]['total_ingresos_emi'] = ingresos_emi
        summary[m_key]['total_ingresos_uli'] = ingresos_uli

    return summary
