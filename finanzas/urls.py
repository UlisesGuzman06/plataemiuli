from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('gastos/', views.gastos_list_view, name='gastos_list'),
    path('gastos/eliminar/<int:gasto_id>/', views.eliminar_gasto_view, name='eliminar_gasto'),
    path('gastos-fijos/', views.gastos_fijos_view, name='gastos_fijos'),
    path('gastos-fijos/toggle/<int:gf_id>/', views.toggle_gasto_fijo_view, name='toggle_gasto_fijo'),
    path('balance/', views.balance_view, name='balance'),
    path('ingresos/', views.ingresos_view, name='ingresos'),
    path('cotizaciones/', views.cotizaciones_view, name='cotizaciones'),
]
