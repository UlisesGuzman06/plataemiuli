import os, django, dj_database_url

RENDER_DB_URL = "postgresql://plata_db_tzsl_user:QB73vS6VklEPSlj4XFBrKRLAkTHvwGFe@dpg-d9ho0kupbkes738sg2n0-a.oregon-postgres.render.com/plata_db_tzsl"

os.environ['DATABASE_URL'] = RENDER_DB_URL
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Override settings before django setup
from django.conf import settings
settings.DATABASES['default'] = dj_database_url.config(
    default=RENDER_DB_URL,
    conn_max_age=600,
    ssl_require=True
)

django.setup()

from django.core.management import call_command
print("--- Ejecutando migrate en Render Postgres ---")
call_command('migrate')
print("--- Done ---")
