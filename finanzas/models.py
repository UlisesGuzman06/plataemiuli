from django.db import models
from django.utils import timezone

class Persona(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color_hex = models.CharField(max_length=7, default="#ec4899")  # Rose accent default

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
    EXACT_AMOUNT = 'EXACT', 'Montos Exactos por Persona'
    PERCENTAGE = 'PERCENT', 'Porcentaje Personalizado'
    PAID_FOR_OTHER = 'FOR_OTHER', '100% Pagado para la Otra Persona'
    PERSONAL = 'PERSONAL', '100% Personal (No se comparte)'


class Moneda(models.TextChoices):
    ARS = 'ARS', 'Pesos ($ ARS)'
    USD = 'USD', 'Dólares (US$ USD)'


class Gasto(models.Model):
    descripcion = models.CharField(max_length=200)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.ARS)
    fecha = models.DateField(default=timezone.now)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='gastos')
    pagado_por = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='gastos_pagados')
    
    tipo_division = models.CharField(max_length=10, choices=TipoDivision.choices, default=TipoDivision.EQUITY_50_50)
    
    # Responsabilidad de gasto (cuánto le corresponde a cada uno del costo total)
    monto_emi = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_uli = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    porcentaje_emi = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)

    # Para casos donde ambos ponen efectivo/transferencia al pagar
    monto_pagado_emi = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_pagado_uli = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notas = models.TextField(blank=True, default='')
    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calculate split amounts before saving if needed
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
        elif self.tipo_division == TipoDivision.PAID_FOR_OTHER:
            # If Emi paid, Uli owes 100% of it (so Uli responsibility = total)
            if self.pagado_por.slug == 'emi':
                self.monto_emi = 0
                self.monto_uli = total
            else:
                self.monto_emi = total
                self.monto_uli = 0
        elif self.tipo_division == TipoDivision.PERSONAL:
            if self.pagado_por.slug == 'emi':
                self.monto_emi = total
                self.monto_uli = 0
            else:
                self.monto_emi = 0
                self.monto_uli = total

        # Handle pagado por amounts default
        if self.monto_pagado_emi == 0 and self.monto_pagado_uli == 0:
            if self.pagado_por.slug == 'emi':
                self.monto_pagado_emi = total
                self.monto_pagado_uli = 0
            else:
                self.monto_pagado_emi = 0
                self.monto_pagado_uli = total

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion} - ${self.monto_total} ({self.moneda})"

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
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.ARS)
    dia_vencimiento = models.IntegerField(default=10)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    responsable = models.CharField(max_length=15, choices=ResponsableFijo.choices, default=ResponsableFijo.COMPARTIDO)
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.nombre} (${self.monto_estimado}) - Día {self.dia_vencimiento}"

    class Meta:
        verbose_name = "Gasto Fijo"
        verbose_name_plural = "Gastos Fijos"
        ordering = ['dia_vencimiento']


class Ingreso(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='ingresos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.ARS)
    descripcion = models.CharField(max_length=200)
    fecha = models.DateField(default=timezone.now)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.persona.nombre} - ${self.monto} ({self.descripcion})"

    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ['-fecha', '-creado_en']


class PagoSaldo(models.Model):
    pagador = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='pagos_realizados')
    receptor = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='pagos_recibidos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.ARS)
    fecha = models.DateField(default=timezone.now)
    notas = models.TextField(blank=True, default='')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ajuste: {self.pagador.nombre} ➔ {self.receptor.nombre} (${self.monto} {self.moneda})"

    class Meta:
        verbose_name = "Pago de Saldo"
        verbose_name_plural = "Pagos de Saldo"
        ordering = ['-fecha', '-creado_en']
