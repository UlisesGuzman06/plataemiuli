from django.core.management.base import BaseCommand
from finanzas.models import Persona

class Command(BaseCommand):
    help = 'Seeds initial essential personas for Emi & Uli'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Seeding Plata Emi y Uli essential data...'))

        # Personas
        Persona.objects.get_or_create(nombre='Emi', slug='emi', defaults={'color_hex': '#ec4899'})
        Persona.objects.get_or_create(nombre='Uli', slug='uli', defaults={'color_hex': '#6366f1'})

        self.stdout.write(self.style.SUCCESS('Successfully seeded Plata Emi y Uli!'))
