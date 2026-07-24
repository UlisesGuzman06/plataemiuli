import os
import django
import dj_database_url

RENDER_DB_URL = "postgresql://plata_db_tzsl_user:QB73vS6VklEPSlj4XFBrKRLAkTHvwGFe@dpg-d9ho0kupbkes738sg2n0-a.oregon-postgres.render.com/plata_db_tzsl"

print("--- Paso 1: Leyendo toda la data local de SQLite ---")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finanzas.models import Persona, Gasto, GastoFijo

personas_local = list(Persona.objects.all().values())
gastos_local = list(Gasto.objects.all().values())
gastos_fijos_local = list(GastoFijo.objects.all().values())

print(f"Data local SQLite: {len(personas_local)} Personas, {len(gastos_local)} Gastos, {len(gastos_fijos_local)} Gastos Fijos.")

print("\n--- Paso 2: Conectando a PostgreSQL en Render ---")

from django.conf import settings
from django.db import connections

# Override default database connection with Postgres URL
settings.DATABASES['default'] = dj_database_url.config(
    default=RENDER_DB_URL,
    conn_max_age=600,
    ssl_require=True
)

# Close existing sqlite connection and reconnect to Postgres
connections['default'].close()

# Executing raw SQL table fixes to ensure columns exist in Postgres
with connections['default'].cursor() as cursor:
    cursor.execute("ALTER TABLE finanzas_gasto ADD COLUMN IF NOT EXISTS es_tarjeta BOOLEAN DEFAULT FALSE;")
    cursor.execute("ALTER TABLE finanzas_gastofijo ADD COLUMN IF NOT EXISTS es_cuota BOOLEAN DEFAULT FALSE;")
    cursor.execute("ALTER TABLE finanzas_gastofijo ADD COLUMN IF NOT EXISTS cuotas_totales INTEGER NULL;")
    cursor.execute("ALTER TABLE finanzas_gastofijo ADD COLUMN IF NOT EXISTS cuotas_restantes INTEGER NULL;")
    cursor.execute("ALTER TABLE finanzas_gastofijo ADD COLUMN IF NOT EXISTS fecha_fin_cuota DATE NULL;")
    cursor.execute("ALTER TABLE finanzas_gasto DROP COLUMN IF EXISTS categoria_id;")
    cursor.execute("ALTER TABLE finanzas_gastofijo DROP COLUMN IF EXISTS categoria_id;")

from django.core.management import call_command
call_command('migrate', fake=True)

print("\n--- Paso 3: Rellenando PostgreSQL en Render con la data exacta ---")
from finanzas.models import Persona as PG_Persona, Gasto as PG_Gasto, GastoFijo as PG_GastoFijo

PG_Gasto.objects.all().delete()
PG_GastoFijo.objects.all().delete()

for p in personas_local:
    PG_Persona.objects.update_or_create(
        id=p['id'],
        defaults={
            'nombre': p['nombre'],
            'slug': p['slug'],
            'color_hex': p['color_hex'],
        }
    )

for gf in gastos_fijos_local:
    PG_GastoFijo.objects.create(
        id=gf['id'],
        nombre=gf['nombre'],
        monto_estimado=gf['monto_estimado'],
        dia_vencimiento=gf['dia_vencimiento'],
        responsable=gf['responsable'],
        es_cuota=gf['es_cuota'],
        cuotas_totales=gf['cuotas_totales'],
        cuotas_restantes=gf['cuotas_restantes'],
        fecha_fin_cuota=gf['fecha_fin_cuota'],
        activo=gf['activo'],
        notas=gf['notas'],
    )

for g in gastos_local:
    PG_Gasto.objects.create(
        id=g['id'],
        descripcion=g['descripcion'],
        monto_total=g['monto_total'],
        fecha=g['fecha'],
        pagado_por_id=g['pagado_por_id'],
        tipo_division=g['tipo_division'],
        monto_emi=g['monto_emi'],
        monto_uli=g['monto_uli'],
        porcentaje_emi=g['porcentaje_emi'],
        es_tarjeta=g['es_tarjeta'],
        notas=g['notas'],
    )

p_res = PG_Persona.objects.count()
g_res = PG_Gasto.objects.count()
gf_res = PG_GastoFijo.objects.count()

print(f"\n[OK] ¡EXITO COMPLETO! PostgreSQL en Render ahora tiene:")
print(f"  - {p_res} Personas")
print(f"  - {g_res} Gastos")
print(f"  - {gf_res} Gastos Fijos")
