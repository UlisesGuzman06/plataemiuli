import os, django, dj_database_url

RENDER_DB_URL = "postgresql://plata_db_tzsl_user:QB73vS6VklEPSlj4XFBrKRLAkTHvwGFe@dpg-d9ho0kupbkes738sg2n0-a.oregon-postgres.render.com/plata_db_tzsl"

os.environ['DATABASE_URL'] = RENDER_DB_URL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finanzas.models import Persona, Gasto, GastoFijo

p_count = Persona.objects.count()
g_count = Gasto.objects.count()
gf_count = GastoFijo.objects.count()

print(f"PostgreSQL en Render contiene:")
print(f" - {p_count} Personas")
print(f" - {g_count} Gastos")
print(f" - {gf_count} Gastos Fijos")

print("\n--- Primeros 5 Gastos en Postgres ---")
for g in Gasto.objects.all()[:5]:
    print(f"  [ID {g.id}] {g.descripcion} | Total: ${g.monto_total} | Emi: ${g.monto_emi} | Uli: ${g.monto_uli} | Tarjeta: {g.es_tarjeta}")

print("\n--- Gastos Fijos en Postgres ---")
for gf in GastoFijo.objects.all():
    print(f"  [ID {gf.id}] {gf.nombre} | Monto: ${gf.monto_estimado} | Día: {gf.dia_vencimiento} | Resp: {gf.responsable}")
