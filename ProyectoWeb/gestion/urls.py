from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('alumnos/', views.alumnos, name='alumnos'),
    path('alumnos/<int:alumno_id>/', views.detalle_alumno, name='detalle_alumno'),
    path('horarios/', views.horarios, name='horarios'),
    path('horarios/<int:horario_id>/', views.detalle_horario, name='detalle_horario'),
    path('sesiones/<int:sesion_id>/asistencias/', views.detalle_asistencias, name='detalle_asistencias'),
    path('pagos/', views.pagos, name='pagos'),
    path('sesiones/', views.sesiones, name='sesiones'),
    path('gastos/', views.gastos, name='gastos'),
    path('reportes/', views.reportes, name='reportes'),
    path('api/alumnos-por-horario/', views.get_alumnos_por_horario, name='alumnos_por_horario'),
] 