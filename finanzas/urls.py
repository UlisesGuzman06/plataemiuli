from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('editar/<int:gasto_id>/', views.editar_gasto_view, name='editar_gasto'),
    path('eliminar/<int:gasto_id>/', views.eliminar_gasto_view, name='eliminar_gasto'),
    path('gastos-fijos/', views.gastos_fijos_view, name='gastos_fijos'),
    path('gastos-fijos/editar/<int:gf_id>/', views.editar_gasto_fijo_view, name='editar_gasto_fijo'),
    path('gastos-fijos/toggle/<int:gf_id>/', views.toggle_gasto_fijo_view, name='toggle_gasto_fijo'),
    path('gastos-fijos/descontar-cuota/<int:gf_id>/', views.descontar_cuota_view, name='descontar_cuota'),
    path('gastos-fijos/eliminar/<int:gf_id>/', views.eliminar_gasto_fijo_view, name='eliminar_gasto_fijo'),
    path('cotizaciones/', views.cotizaciones_view, name='cotizaciones'),
]
