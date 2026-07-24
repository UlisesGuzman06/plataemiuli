from django.contrib import admin
from .models import Persona, Categoria, Gasto, GastoFijo, Ingreso, PagoSaldo

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'slug', 'color_hex')
    search_fields = ('nombre', 'slug')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'icono', 'nombre', 'color')
    search_fields = ('nombre',)

@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'descripcion', 'monto_total', 'moneda', 'pagado_por', 'tipo_division', 'monto_emi', 'monto_uli')
    list_filter = ('moneda', 'pagado_por', 'tipo_division', 'categoria', 'fecha')
    search_fields = ('descripcion', 'notas')
    date_hierarchy = 'fecha'

@admin.register(GastoFijo)
class GastoFijoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'monto_estimado', 'moneda', 'dia_vencimiento', 'responsable', 'activo')
    list_filter = ('moneda', 'responsable', 'activo')
    search_fields = ('nombre',)

@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'persona', 'descripcion', 'monto', 'moneda')
    list_filter = ('persona', 'moneda', 'fecha')
    search_fields = ('descripcion',)

@admin.register(PagoSaldo)
class PagoSaldoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'pagador', 'receptor', 'monto', 'moneda')
    list_filter = ('moneda', 'fecha')
    search_fields = ('notas',)
