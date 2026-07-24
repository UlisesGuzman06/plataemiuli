from django.contrib import admin
from .models import Persona, Gasto, GastoFijo

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'slug', 'color_hex')
    search_fields = ('nombre', 'slug')

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'descripcion', 'monto_total', 'tipo_division', 'monto_emi', 'monto_uli')
    list_filter = ('tipo_division', 'fecha')
    search_fields = ('descripcion', 'notas')
    date_hierarchy = 'fecha'

@admin.register(GastoFijo)
class GastoFijoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'monto_estimado', 'dia_vencimiento', 'responsable', 'es_cuota', 'cuotas_totales', 'cuotas_restantes', 'fecha_fin_cuota', 'activo')
    list_filter = ('responsable', 'es_cuota', 'activo')
    search_fields = ('nombre',)
