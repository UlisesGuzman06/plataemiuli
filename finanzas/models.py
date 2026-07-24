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


class TipoDivision(models.TextChoices):
    EQUITY_50_50 = '50_50', 'Ambos'
    EMI_PERSONAL = 'EMI', 'Emi'
    ULI_PERSONAL = 'ULI', 'Uli'
    EXACT_AMOUNT = 'EXACT', 'Montos Exactos'


class Gasto(models.Model):
    descripcion = models.CharField(max_length=200)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    pagado_por = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='gastos_pagados', null=True, blank=True)
    
    tipo_division = models.CharField(max_length=10, choices=TipoDivision.choices, default=TipoDivision.EQUITY_50_50)
    
    monto_emi = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_uli = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    porcentaje_emi = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)

    # Pago con tarjeta o efectivo/transferencia
    es_tarjeta = models.BooleanField(default=False, verbose_name="Pagado con Tarjeta")

    notas = models.TextField(blank=True, default='')
    creado_en = models.DateTimeField(auto_now_add=True)

    @property
    def badge_style(self):
        if self.tipo_division == 'EMI':
            return 'background:rgba(236, 72, 153, 0.25); color:#f472b6; border:1px solid rgba(236, 72, 153, 0.5);'
        elif self.tipo_division == 'ULI':
            return 'background:rgba(99, 102, 241, 0.25); color:#818cf8; border:1px solid rgba(99, 102, 241, 0.5);'
        elif self.tipo_division == '50_50':
            return 'background:rgba(52, 211, 153, 0.25); color:#34d399; border:1px solid rgba(52, 211, 153, 0.5);'
        return 'background:rgba(251, 191, 36, 0.25); color:#fbbf24; border:1px solid rgba(251, 191, 36, 0.5);'

    def save(self, *args, **kwargs):
        if not self.pagado_por:
            self.pagado_por = Persona.objects.first()

        total = self.monto_total or 0
        if self.tipo_division == TipoDivision.EQUITY_50_50:
            half = total / 2
            self.monto_emi = half
            self.monto_uli = half
            self.porcentaje_emi = 50.00
        elif self.tipo_division == TipoDivision.EMI_PERSONAL:
            self.monto_emi = total
            self.monto_uli = 0
            self.porcentaje_emi = 100.00
        elif self.tipo_division == TipoDivision.ULI_PERSONAL:
            self.monto_emi = 0
            self.monto_uli = total
            self.porcentaje_emi = 0.00

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion} - ${self.monto_total}"

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['-fecha', '-creado_en']


class ResponsableFijo(models.TextChoices):
    AMBOS = 'COMPARTIDO', 'Ambos'
    ULI = 'ULI', 'Uli'
    EMI = 'EMI', 'Emi'


class GastoFijo(models.Model):
    nombre = models.CharField(max_length=100)
    monto_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    dia_vencimiento = models.IntegerField(default=1)
    responsable = models.CharField(max_length=15, choices=ResponsableFijo.choices, default=ResponsableFijo.AMBOS)
    
    # Sistema de Cuotas
    es_cuota = models.BooleanField(default=False)
    cuotas_totales = models.IntegerField(null=True, blank=True, default=None)
    cuotas_restantes = models.IntegerField(null=True, blank=True, default=None)
    fecha_fin_cuota = models.DateField(null=True, blank=True, help_text="Fecha o mes de finalización de la cuota")

    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, default='')

    @property
    def badge_style(self):
        if self.responsable == 'EMI':
            return 'background:rgba(236, 72, 153, 0.25); color:#f472b6; border:1px solid rgba(236, 72, 153, 0.5);'
        elif self.responsable == 'ULI':
            return 'background:rgba(99, 102, 241, 0.25); color:#818cf8; border:1px solid rgba(99, 102, 241, 0.5);'
        return 'background:rgba(52, 211, 153, 0.25); color:#34d399; border:1px solid rgba(52, 211, 153, 0.5);'

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
