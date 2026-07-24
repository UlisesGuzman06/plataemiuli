from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='punto_monto')
def punto_monto(value):
    """
    Formats a number with Argentine thousands separators (dot '.') and decimals (comma ',').
    Example: 172151.80 -> "172.151,80", 445000 -> "445.000"
    """
    if value is None or value == '':
        return "0"
    try:
        val = Decimal(str(value))
        # Format with 2 decimals
        formatted = f"{val:,.2f}"  # e.g., "172,151.80"
        # Swap comma and dot for Argentine style
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        # Strip trailing ,00 for clean integers
        if formatted.endswith(',00'):
            formatted = formatted[:-3]
        return formatted
    except Exception:
        return str(value)
