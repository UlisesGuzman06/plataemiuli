from django.db import models
from django.utils import timezone

class Persona(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color_hex = models.CharField(max_length=7, default="#ec4899")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    icono = models.CharField(max_length=10, default="📦")
    color = models.CharField(max_length=7, default="#94a3b8")

    def __str__(self):
        return f"{self.icono} {self.nombre}"

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']


class TipoDivision(models.TextChoices):
    EQUITY_50_50 = '50_50', 'Mitad y Mitad (50 / 50)'
    EXACT_AMOUNT = 'EXACT', 'Montos Exactos'
    PERCENTAGE = 'PERCENT', 'Porcentaje Personalizado'


class Gasto(models.Model):
    descripcion = models.CharField(max_length=200)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos')
    pagado_por = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='gastos_pagados', null=True, blank=True)
    
    tipo_division = models.CharField(max_length=10, choices=TipoDivision.choices, default=TipoDivision.EQUITY_50_50)
    
    monto_emi = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_uli = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    porcentaje_emi = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)

    notas = models.TextField(blank=True, default='')
    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pagado_por:
            self.pagado_por = Persona.objects.first()

        total = self.monto_total or 0
        if self.tipo_division == TipoDivision.EQUITY_50_50:
            half = total / 2
            self.monto_emi = half
            self.monto_uli = half
            self.porcentaje_emi = 50.00
        elif self.tipo_division == TipoDivision.PERCENTAGE:
            pct_emi = self.porcentaje_emi or 50.00
            self.monto_emi = round(total * (pct_emi / 100), 2)
            self.monto_uli = round(total - self.monto_emi, 2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion} - ${self.monto_total}"

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['-fecha', '-creado_en']


class ResponsableFijo(models.TextChoices):
    EMI = 'EMI', 'Emi'
    ULI = 'ULI', 'Uli'
    COMPARTIDO = 'COMPARTIDO', 'Compartido (50/50)'


class GastoFijo(models.Model):
    nombre = models.CharField(max_length=100)
    monto_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    dia_vencimiento = models.IntegerField(default=1)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    responsable = models.CharField(max_length=15, choices=ResponsableFijo.choices, default=ResponsableFijo.COMPARTIDO)
    
    # Sistema de Cuotas
    es_cuota = models.BooleanField(default=False)
    cuotas_totales = models.IntegerField(null=True, blank=True, default=None)
    cuotas_restantes = models.IntegerField(null=True, blank=True, default=None)
    fecha_fin_cuota = models.DateField(null=True, blank=True, help_text="Fecha o mes de finalización de la cuota")

    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, default='')

    def cuota_actual(self):
        if self.es_cuota and self.cuotas_totales and self.cuotas_restantes is not None:
            return (self.cuotas_totales - self.cuotas_restantes) + 1
        return None

    def descollar_cuota(self):
        if self.es_cuota and self.cuotas_restantes is not None and self.cuotas_restantes > 0:
            self.cuotas_restantes -= 1
            if self.cuotas_restantes == 0:
                self.activo = False
            self.save()

    def __str__(self):
        cuota_str = f" ({self.cuota_actual()}/{self.cuotas_totales})" if self.es_cuota else ""
        return f"{self.nombre}{cuota_str} - ${self.monto_estimado}"

    class Meta:
        verbose_name = "Gasto Fijo"
        verbose_name_plural = "Gastos Fijos"
        ordering = ['dia_vencimiento']
