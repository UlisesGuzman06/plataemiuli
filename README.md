# 💸 Plata Emi & Uli - Gestión Financiera

Sistema de gestión de finanzas compartidas e individuales para **Emi y Uli**, desarrollado con **Django** y plantillas HTML/CSS en modo oscuro con paleta en Gris, Rosado y Blanco.

## 🚀 Características
- **División de Gastos Avanzada**: 50/50, montos exactos, porcentajes personalizados, 100% para el otro, o 100% personal.
- **Balance & Ajustes (`/balance/`)**: Cálculo automático de deudas cruzadas y registro de liquidaciones.
- **Gastos Fijos (`/gastos-fijos/`)**: Gestión de cuentas mensuales recurrentes y vencimientos.
- **Cotizaciones en Vivo (`/cotizaciones/`)**: Integración con DolarApi.com (Dólar Blue, MEP, Oficial) y conversor de moneda.
- **Ingresos (`/ingresos/`)**: Seguimiento de sueldos y aportes.

## 🛠️ Cómo Ejecutar
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver 8000
```
