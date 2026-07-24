from django.core.management.base import BaseCommand
from decimal import Decimal
from finanzas.models import Persona, Categoria, GastoFijo, ResponsableFijo

class Command(BaseCommand):
    help = 'Seeds initial essential categories and personas for Emi & Uli'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Seeding Plata Emi y Uli essential data...'))

        # 1. Personas
        Persona.objects.get_or_create(nombre='Emi', slug='emi', defaults={'color_hex': '#ec4899'})
        Persona.objects.get_or_create(nombre='Uli', slug='uli', defaults={'color_hex': '#6366f1'})

        # 2. Categorías
        cats_data = [
          ('Supermercado', '🛒', '#ec4899'),
          ('Alquiler', '🏠', '#f43f5e'),
          ('Servicios', '💡', '#eab308'),
          ('Salidas/Comida', '🍔', '#f97316'),
          ('Transporte', '🚗', '#06b6d4'),
          ('Gustitos', '🎁', '#a855f7'),
          ('Inversiones', '📈', '#10b981'),
          ('Varios', '📦', '#64748b'),
        ]

        for nombre, icono, color in cats_data:
            Categoria.objects.get_or_create(nombre=nombre, defaults={'icono': icono, 'color': color})

        self.stdout.write(self.style.SUCCESS('Successfully seeded Plata Emi y Uli!'))
