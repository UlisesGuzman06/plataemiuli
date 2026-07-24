import requests
from decimal import Decimal
from .models import Persona, Gasto, GastoFijo, TipoDivision, ResponsableFijo

DOLAR_API_URL = "https://dolarapi.com/v1/dolares"

_rates_cache = None
_rates_timestamp = 0

def get_dolar_rates():
    """Fetch live dollar rates from DolarApi.com with graceful fallback."""
    global _rates_cache, _rates_timestamp
    import time
    now = time.time()
    if _rates_cache and (now - _rates_timestamp < 300):
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

    return {
        'blue': {'nombre': 'Dólar Blue', 'compra': 1380.0, 'venta': 1400.0},
        'bolsa': {'nombre': 'Dólar MEP', 'compra': 1360.0, 'venta': 1375.0},
        'oficial': {'nombre': 'Dólar Oficial', 'compra': 940.0, 'venta': 980.0},
    }


def calculate_financial_summary(year=None, month=None):
    """
    Complete financial summary combining monthly variable expenses and active fixed expenses.
    """
    summary = {
        'total_gastos': Decimal('0.00'),       # Variables total
        'total_emi': Decimal('0.00'),          # Variables Emi
        'total_uli': Decimal('0.00'),          # Variables Uli
        
        'total_fijos': Decimal('0.00'),        # Fijos total
        'total_fijos_emi': Decimal('0.00'),    # Fijos Emi
        'total_fijos_uli': Decimal('0.00'),    # Fijos Uli

        'gran_total': Decimal('0.00'),         # Variables + Fijos total
        'gran_total_emi': Decimal('0.00'),     # Variables Emi + Fijos Emi
        'gran_total_uli': Decimal('0.00'),     # Variables Uli + Fijos Uli
    }

    # 1. Variables del mes
    gastos = Gasto.objects.all()
    if year and month:
        gastos = gastos.filter(fecha__year=year, fecha__month=month)

    for g in gastos:
        summary['total_gastos'] += g.monto_total
        summary['total_emi'] += g.monto_emi
        summary['total_uli'] += g.monto_uli

    # 2. Gastos Fijos activos
    gastos_fijos = GastoFijo.objects.filter(activo=True)
    for gf in gastos_fijos:
        monto = gf.monto_estimado
        summary['total_fijos'] += monto

        if gf.responsable == ResponsableFijo.EMI:
            summary['total_fijos_emi'] += monto
        elif gf.responsable == ResponsableFijo.ULI:
            summary['total_fijos_uli'] += monto
        else: # COMPARTIDO
            half = monto / 2
            summary['total_fijos_emi'] += half
            summary['total_fijos_uli'] += half

    # 3. Gran Total (Fijos + Variables)
    summary['gran_total'] = summary['total_gastos'] + summary['total_fijos']
    summary['gran_total_emi'] = summary['total_emi'] + summary['total_fijos_emi']
    summary['gran_total_uli'] = summary['total_uli'] + summary['total_fijos_uli']

    return summary
