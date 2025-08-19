from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.reportes, name='reportes'),
    path('exportar-alumnos/', views.exportar_alumnos_excel, name='exportar_alumnos'),
    path('exportar-pagos/', views.exportar_pagos_excel, name='exportar_pagos'),
    path('exportar-asistencias/', views.exportar_asistencias_excel, name='exportar_asistencias'),
    path('exportar-gastos/', views.exportar_gastos_excel, name='exportar_gastos'),
] 