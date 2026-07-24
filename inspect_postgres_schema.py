import psycopg2

conn = psycopg2.connect("postgresql://plata_db_tzsl_user:QB73vS6VklEPSlj4XFBrKRLAkTHvwGFe@dpg-d9ho0kupbkes738sg2n0-a.oregon-postgres.render.com/plata_db_tzsl")
cur = conn.cursor()

print("--- 1. Triggers en finanzas_gasto ---")
cur.execute("""
    SELECT trigger_name, event_manipulation, action_statement 
    FROM information_schema.triggers 
    WHERE event_object_table = 'finanzas_gasto';
""")
triggers = cur.fetchall()
print("Triggers:", triggers)

print("\n--- 2. Views en la base de datos ---")
cur.execute("""
    SELECT table_name 
    FROM information_schema.views 
    WHERE table_schema = 'public';
""")
views = cur.fetchall()
print("Views:", views)

print("\n--- 3. Reglas o Indices en finanzas_gasto ---")
cur.execute("""
    SELECT indexname, indexdef 
    FROM pg_indexes 
    WHERE tablename = 'finanzas_gasto';
""")
indexes = cur.fetchall()
for idx in indexes:
    print(" ", idx)

print("\n--- 4. Drop table y recrear tablas desde cero si fuera necesario ---")

cur.close()
conn.close()
