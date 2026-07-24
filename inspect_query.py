import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finanzas.models import Gasto, GastoFijo, Persona

print("--- SQL Query de Gasto.objects.all() ---")
print(str(Gasto.objects.all().query))

print("\n--- SQL Query de GastoFijo.objects.all() ---")
print(str(GastoFijo.objects.all().query))
