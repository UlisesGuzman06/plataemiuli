from django import template

register = template.Library()

@register.filter(name='punto_monto')
def punto_monto(value):
    if value is None or value == '':
        return "0"
    try:
        val = float(value)
        # Formato con miles separados por puntos (ej: 10000 -> 10.000, 172151.80 -> 172.151,80)
        parts = f"{val:,.2f}".split('.')
        integer_part = parts[0].replace(',', '.')
        decimal_part = parts[1]
        if decimal_part == '00':
            return integer_part
        return f"{integer_part},{decimal_part}"
    except Exception:
        return str(value)
