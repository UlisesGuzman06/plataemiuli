import psycopg2

conn = psycopg2.connect("postgresql://plata_db_tzsl_user:QB73vS6VklEPSlj4XFBrKRLAkTHvwGFe@dpg-d9ho0kupbkes738sg2n0-a.oregon-postgres.render.com/plata_db_tzsl")
cur = conn.cursor()

print("--- 1. Testing raw query SELECT * FROM finanzas_gasto ---")
try:
    cur.execute('SELECT "finanzas_gasto"."id", "finanzas_gasto"."descripcion", "finanzas_gasto"."monto_total", "finanzas_gasto"."fecha", "finanzas_gasto"."pagado_por_id", "finanzas_gasto"."tipo_division", "finanzas_gasto"."monto_emi", "finanzas_gasto"."monto_uli", "finanzas_gasto"."porcentaje_emi", "finanzas_gasto"."es_tarjeta", "finanzas_gasto"."notas", "finanzas_gasto"."creado_en" FROM "finanzas_gasto" ORDER BY "finanzas_gasto"."fecha" DESC, "finanzas_gasto"."creado_en" DESC;')
    rows = cur.fetchall()
    print("ÉXITO! Filas obtenidas:", len(rows))
except Exception as e:
    print("ERROR al ejecutar la query exacta:", e)

conn.close()
