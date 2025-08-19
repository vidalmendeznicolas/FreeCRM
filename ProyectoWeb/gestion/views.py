from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q, Count
from django.utils.dateparse import parse_date
from django.http import JsonResponse

from .models import Alumno, Pago, Horario, Sesion, Profesor, Gasto

@login_required(login_url='login:login')
def inicio(request):
    """Dashboard principal con estadísticas"""
    # Contar registros
    alumnos_count = Alumno.objects.filter(activo=True).count()
    pagos_count = Pago.objects.count()
    horarios_count = Horario.objects.filter(activo=True).count()
    sesiones_count = Sesion.objects.count()
    gastos_count = Gasto.objects.count()
    
    # Estadísticas de pagos del mes actual
    now = timezone.now()
    pagos_mes = Pago.objects.filter(
        fecha__month=now.month,
        fecha__year=now.year
    ).aggregate(total=Sum('importe_final'))['total'] or 0
    
    # Gastos del mes actual
    gastos_mes = Gasto.objects.filter(
        fecha_gasto__month=now.month,
        fecha_gasto__year=now.year
    ).aggregate(total=Sum('importe'))['total'] or 0
    
    # Balance del mes (ingresos - gastos)
    balance_mes = pagos_mes - gastos_mes
    
    context = {
        'titulo': 'Dashboard de Gestión',
        'alumnos_count': alumnos_count,
        'pagos_count': pagos_count,
        'horarios_count': horarios_count,
        'sesiones_count': sesiones_count,
        'gastos_count': gastos_count,
        'pagos_mes': pagos_mes,
        'gastos_mes': gastos_mes,
        'balance_mes': balance_mes,
    }
    return render(request, 'gestion/inicio.html', context)

@login_required(login_url='login:login')
def alumnos(request):
    """Gestión de alumnos con estadísticas completas"""
    from .models import Alumno
    from django.db.models import Count, Sum, Q
    
    # Obtener mes y año actual para filtros
    now = timezone.now()
    mes_actual = now.month
    año_actual = now.year
    
    # Filtros GET
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    curso = request.GET.get('curso', '')
    compartido = request.GET.get('compartido', '')
    
    # Query base
    alumnos_qs = Alumno.objects.all()
    
    # Aplicar filtros
    if q:
        alumnos_qs = alumnos_qs.filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(dni__icontains=q)
        )
    
    if estado:
        alumnos_qs = alumnos_qs.filter(activo=estado == 'activo')
    
    if curso:
        alumnos_qs = alumnos_qs.filter(curso=curso)
    
    if compartido:
        alumnos_qs = alumnos_qs.filter(es_compartido=compartido == 'compartido')
    
    # Calcular estadísticas generales (antes de aplicar filtros de estado)
    alumnos_totales = Alumno.objects.all()
    
    # Aplicar filtros básicos a las estadísticas (sin filtro de estado)
    if q:
        alumnos_totales = alumnos_totales.filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(dni__icontains=q)
        )
    
    # Estadísticas específicas
    total_alumnos = alumnos_totales.count()
    alumnos_activos = alumnos_totales.filter(activo=True).count()
    alumnos_compartidos = alumnos_totales.filter(activo=True, es_compartido=True).count()
    
    # Anotar estadísticas para cada alumno
    alumnos_con_stats = []
    for alumno in alumnos_qs:
        # Horarios matriculados activos
        horarios_matriculados = alumno.matriculas.filter(estado='activa').count()
        
        # Asistencias totales (este mes)
        asistencias_este_mes = alumno.asistencias.filter(
            sesion__inicio__month=mes_actual,
            sesion__inicio__year=año_actual,
            presente=True
        ).count()
        
        # No asistencias totales (este mes)
        no_asistencias_este_mes = alumno.asistencias.filter(
            sesion__inicio__month=mes_actual,
            sesion__inicio__year=año_actual,
            presente=False
        ).count()
        
        # Total de sesiones este mes
        total_sesiones_mes = alumno.asistencias.filter(
            sesion__inicio__month=mes_actual,
            sesion__inicio__year=año_actual
        ).count()
        
        # Porcentaje de asistencia este mes
        porcentaje_asistencia = 0
        if total_sesiones_mes > 0:
            porcentaje_asistencia = round((asistencias_este_mes / total_sesiones_mes) * 100, 1)
        
        # Pagos este mes
        pagos_este_mes = alumno.pago_set.filter(
            fecha__month=mes_actual,
            fecha__year=año_actual
        ).aggregate(
            total_pagado=Sum('importe_final')
        )['total_pagado'] or 0
        
        # Último pago
        ultimo_pago = alumno.pago_set.order_by('-fecha').first()
        
        # Próxima sesión
        proxima_sesion = None
        for matricula in alumno.matriculas.filter(estado='activa'):
            proxima = matricula.horario.sesiones.filter(
                inicio__gte=now
            ).order_by('inicio').first()
            if proxima and (proxima_sesion is None or proxima.inicio < proxima_sesion.inicio):
                proxima_sesion = proxima
        
        alumnos_con_stats.append({
            'alumno': alumno,
            'horarios_matriculados': horarios_matriculados,
            'asistencias_este_mes': asistencias_este_mes,
            'no_asistencias_este_mes': no_asistencias_este_mes,
            'total_sesiones_mes': total_sesiones_mes,
            'porcentaje_asistencia': porcentaje_asistencia,
            'pagos_este_mes': pagos_este_mes,
            'ultimo_pago': ultimo_pago,
            'proxima_sesion': proxima_sesion,
        })
    
    # Ordenar por apellido
    alumnos_con_stats.sort(key=lambda x: (x['alumno'].apellido, x['alumno'].nombre))
    
    context = {
        'titulo': 'Gestión de Alumnos',
        'alumnos': alumnos_con_stats,
        'total_alumnos': total_alumnos,
        'alumnos_activos': alumnos_activos,
        'alumnos_compartidos': alumnos_compartidos,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'filters': {
            'q': q,
            'estado': estado,
            'curso': curso,
            'compartido': compartido,
        }
    }
    return render(request, 'gestion/alumnos.html', context)

@login_required(login_url='login:login')
def pagos(request):
    """Listado y resumen de pagos con filtros básicos"""
    from .models import Alumno
    from datetime import datetime
    
    pagos_all = (Pago.objects
                .select_related('alumno', 'profesor')
                .order_by('-fecha', '-id'))

    # Totales globales (sin filtros)
    total_general_all = pagos_all.aggregate(total=Sum('importe_final'))['total'] or 0

    # Obtener mes y año actual
    now = timezone.now()
    mes_actual = now.month
    año_actual = now.year

    # Alumnos pendientes de pago (que NO tienen pagos en el mes actual)
    alumnos_activos = Alumno.objects.filter(activo=True)
    alumnos_con_pago_mes = pagos_all.filter(
        fecha__month=mes_actual,
        fecha__year=año_actual
    ).values_list('alumno_id', flat=True).distinct()
    
    alumnos_pendientes_raw = alumnos_activos.exclude(id__in=alumnos_con_pago_mes)
    
    # Añadir información del último pago para cada alumno pendiente
    alumnos_pendientes = []
    for alumno in alumnos_pendientes_raw:
        ultimo_pago = alumno.pago_set.order_by('-fecha').first()
        alumnos_pendientes.append({
            'alumno': alumno,
            'ultimo_pago': ultimo_pago,
        })

    # Filtros GET
    q = (request.GET.get('q') or '').strip()
    desde_raw = (request.GET.get('desde') or '').strip()
    hasta_raw = (request.GET.get('hasta') or '').strip()
    imp_min_raw = (request.GET.get('imp_min') or '').strip()
    imp_max_raw = (request.GET.get('imp_max') or '').strip()

    pagos_qs = pagos_all
    if q:
        pagos_qs = pagos_qs.filter(
            Q(numero__icontains=q) |
            Q(concepto__icontains=q) |
            Q(alumno__nombre__icontains=q) |
            Q(alumno__apellido__icontains=q) |
            Q(profesor__user__first_name__icontains=q) |
            Q(profesor__user__last_name__icontains=q)
        )

    if desde_raw:
        desde = parse_date(desde_raw)
        if desde:
            pagos_qs = pagos_qs.filter(fecha__gte=desde)
    if hasta_raw:
        hasta = parse_date(hasta_raw)
        if hasta:
            pagos_qs = pagos_qs.filter(fecha__lte=hasta)

    try:
        if imp_min_raw:
            pagos_qs = pagos_qs.filter(importe_final__gte=float(imp_min_raw))
        if imp_max_raw:
            pagos_qs = pagos_qs.filter(importe_final__lte=float(imp_max_raw))
    except ValueError:
        messages.warning(request, 'Rangos de importe inválidos. Se ignoraron los filtros de importe.')

    hoy = timezone.localdate()
    total_hoy = pagos_qs.filter(fecha=hoy).aggregate(total=Sum('importe_final'))['total'] or 0
    total_filtrado = pagos_qs.aggregate(total=Sum('importe_final'))['total'] or 0

    context = {
        'titulo': 'Gestión de Pagos',
        'pagos': pagos_qs,
        'alumnos_pendientes': alumnos_pendientes,
        'total_hoy': total_hoy,
        'total_filtrado': total_filtrado,
        'total_general_all': total_general_all,
        'fecha_hoy': hoy,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        # mantener valores en el formulario
        'filters': {
            'q': q,
            'desde': desde_raw,
            'hasta': hasta_raw,
            'imp_min': imp_min_raw,
            'imp_max': imp_max_raw,
        }
    }
    return render(request, 'gestion/pagos.html', context)

def get_alumnos_por_horario(request):
    """Vista AJAX para obtener alumnos matriculados en un horario"""
    if request.method == 'GET' and request.is_ajax():
        horario_id = request.GET.get('horario_id')
        try:
            horario = Horario.objects.get(id=horario_id)
            # Obtener alumnos matriculados activamente
            matriculas = horario.matriculas.filter(estado='activa').select_related('alumno')
            
            alumnos = []
            for matricula in matriculas:
                alumnos.append({
                    'id': matricula.alumno.id,
                    'nombre': f"{matricula.alumno.nombre} {matricula.alumno.apellido}",
                    'dni': matricula.alumno.dni
                })
            
            return JsonResponse({'alumnos': alumnos})
        except Horario.DoesNotExist:
            return JsonResponse({'error': 'Horario no encontrado'}, status=404)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required(login_url='login:login')
def horarios(request):
    """Gestión de horarios con estadísticas completas"""
    from .models import Horario
    from django.db.models import Count, Sum, Q
    
    # Obtener mes y año actual para filtros
    now = timezone.now()
    mes_actual = now.month
    año_actual = now.year
    
    # Filtros GET
    q = request.GET.get('q', '').strip()
    profesor_id = request.GET.get('profesor', '')
    dia_semana = request.GET.get('dia', '')
    activo = request.GET.get('activo', '')
    horario_id = request.GET.get('horario', '')  # Nuevo filtro de horario específico
    
    # Query base
    horarios_qs = Horario.objects.all()
    
    # Aplicar filtros
    if q:
        horarios_qs = horarios_qs.filter(
            Q(asignatura__icontains=q) |
            Q(aula__icontains=q) |
            Q(profesor__user__first_name__icontains=q) |
            Q(profesor__user__last_name__icontains=q)
        )
    
    if profesor_id:
        horarios_qs = horarios_qs.filter(profesor_id=profesor_id)
    
    if dia_semana:
        horarios_qs = horarios_qs.filter(dia_semana=dia_semana)
    
    if activo:
        horarios_qs = horarios_qs.filter(activo=activo == 'activo')
    
    if horario_id:  # Filtrar por horario específico
        horarios_qs = horarios_qs.filter(id=horario_id)
    
    # Calcular estadísticas generales (antes de aplicar filtros de estado)
    horarios_totales = Horario.objects.all()
    
    # Aplicar filtros básicos a las estadísticas (sin filtro de estado)
    if q:
        horarios_totales = horarios_totales.filter(
            Q(asignatura__icontains=q) |
            Q(aula__icontains=q) |
            Q(profesor__user__first_name__icontains=q) |
            Q(profesor__user__last_name__icontains=q)
        )
    
    if profesor_id:
        horarios_totales = horarios_totales.filter(profesor_id=profesor_id)
    
    if dia_semana:
        horarios_totales = horarios_totales.filter(dia_semana=dia_semana)
    
    if horario_id:
        horarios_totales = horarios_totales.filter(id=horario_id)
    
    # Estadísticas específicas
    total_horarios = horarios_totales.count()
    horarios_activos = horarios_totales.filter(activo=True).count()
    
    # Sesiones este mes (suma de todas las sesiones de los horarios filtrados)
    total_sesiones_este_mes = 0
    print(f"DEBUG: Calculando sesiones para mes {mes_actual}/{año_actual}")
    print(f"DEBUG: Horarios totales a revisar: {horarios_totales.count()}")
    
    for horario in horarios_totales:
        sesiones_horario = horario.sesiones.filter(
            inicio__month=mes_actual,
            inicio__year=año_actual
        ).count()
        total_sesiones_este_mes += sesiones_horario
        print(f"DEBUG: Horario {horario.asignatura} - {horario.get_dia_semana_display()} tiene {sesiones_horario} sesiones este mes")
    
    print(f"DEBUG: Total sesiones este mes: {total_sesiones_este_mes}")
    
    # Alternativa: Calcular directamente desde el modelo Sesion
    from .models import Sesion
    total_sesiones_este_mes_alt = Sesion.objects.filter(
        horario__in=horarios_totales,
        inicio__month=mes_actual,
        inicio__year=año_actual
    ).count()
    print(f"DEBUG: Total sesiones (método alternativo): {total_sesiones_este_mes_alt}")
    
    # Usar el método más eficiente
    total_sesiones_este_mes = total_sesiones_este_mes_alt
    
    # Anotar estadísticas para cada horario
    horarios_con_stats = []
    for horario in horarios_qs:
        # Alumnos matriculados activamente
        alumnos_matriculados = horario.matriculas.filter(estado='activa').count()
        
        # Sesiones este mes para este horario específico
        sesiones_este_mes_horario = horario.sesiones.filter(
            inicio__month=mes_actual,
            inicio__year=año_actual
        ).count()
        
        # Asistencias totales este mes
        asistencias_este_mes = horario.sesiones.filter(
            inicio__month=mes_actual,
            inicio__year=año_actual
        ).aggregate(
            total_asistencias=Count('asistencias__id', filter=Q(asistencias__presente=True))
        )['total_asistencias'] or 0
        
        # Próxima sesión
        proxima_sesion = horario.sesiones.filter(
            inicio__gte=now
        ).order_by('inicio').first()
        
        # Última sesión
        ultima_sesion = horario.sesiones.filter(
            inicio__lt=now
        ).order_by('-inicio').first()
        
        # Ocupación del aula (porcentaje de capacidad)
        ocupacion = 0
        if horario.capacidad > 0:
            ocupacion = round((alumnos_matriculados / horario.capacidad) * 100, 1)
        
        horarios_con_stats.append({
            'horario': horario,
            'alumnos_matriculados': alumnos_matriculados,
            'sesiones_este_mes': sesiones_este_mes_horario,
            'asistencias_este_mes': asistencias_este_mes,
            'proxima_sesion': proxima_sesion,
            'ultima_sesion': ultima_sesion,
            'ocupacion': ocupacion,
        })
    
    # Ordenar por día de la semana y hora de inicio
    horarios_con_stats.sort(key=lambda x: (x['horario'].dia_semana, x['horario'].hora_inicio))
    
    # Obtener lista de profesores para el filtro
    from .models import Profesor
    profesores = Profesor.objects.filter(activo=True).order_by('user__first_name', 'user__last_name')
    
    # Obtener lista de todos los horarios para el filtro de horario específico
    todos_horarios = Horario.objects.filter(activo=True).order_by('asignatura', 'dia_semana', 'hora_inicio')
    
    context = {
        'titulo': 'Gestión de Horarios',
        'horarios': horarios_con_stats,
        'profesores': profesores,
        'todos_horarios': todos_horarios,  # Lista para el filtro de horario específico
        'total_horarios': total_horarios,
        'horarios_activos': horarios_activos,
        'sesiones_este_mes': total_sesiones_este_mes,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'filters': {
            'q': q,
            'profesor': profesor_id,
            'dia': dia_semana,
            'activo': activo,
            'horario': horario_id,  # Incluir el filtro de horario en el contexto
        }
    }
    return render(request, 'gestion/horarios.html', context)

@login_required(login_url='login:login')
def sesiones(request):
    """Gestión de sesiones con estadísticas completas"""
    from .models import Sesion, Horario
    from django.db.models import Count, Q
    from django.utils import timezone
    
    # Obtener mes y año actual para filtros
    now = timezone.now()
    mes_actual = now.month
    año_actual = now.year
    
    # Filtros GET
    q = request.GET.get('q', '').strip()
    horario_id = request.GET.get('horario', '')
    profesor_id = request.GET.get('profesor', '')
    estado = request.GET.get('estado', '')  # pasada, futura, hoy
    
    # Query base
    sesiones_qs = Sesion.objects.all()
    
    # Aplicar filtros
    if q:
        sesiones_qs = sesiones_qs.filter(
            Q(horario__asignatura__icontains=q) |
            Q(horario__aula__icontains=q) |
            Q(horario__profesor__user__first_name__icontains=q) |
            Q(horario__profesor__user__last_name__icontains=q)
        )
    
    if horario_id:
        sesiones_qs = sesiones_qs.filter(horario_id=horario_id)
    
    if profesor_id:
        sesiones_qs = sesiones_qs.filter(horario__profesor_id=profesor_id)
    
    if estado:
        if estado == 'pasada':
            sesiones_qs = sesiones_qs.filter(inicio__lt=now)
        elif estado == 'futura':
            sesiones_qs = sesiones_qs.filter(inicio__gte=now)
        elif estado == 'hoy':
            hoy = now.date()
            sesiones_qs = sesiones_qs.filter(inicio__date=hoy)
    
    # Calcular estadísticas generales (antes de aplicar filtros de estado)
    sesiones_totales = Sesion.objects.all()
    
    # Aplicar filtros básicos a las estadísticas (sin filtro de estado)
    if q:
        sesiones_totales = sesiones_totales.filter(
            Q(horario__asignatura__icontains=q) |
            Q(horario__aula__icontains=q) |
            Q(horario__profesor__user__first_name__icontains=q) |
            Q(horario__profesor__user__last_name__icontains=q)
        )
    
    if horario_id:
        sesiones_totales = sesiones_totales.filter(horario_id=horario_id)
    
    if profesor_id:
        sesiones_totales = sesiones_totales.filter(horario__profesor_id=profesor_id)
    
    # Estadísticas específicas
    total_sesiones = sesiones_totales.count()
    sesiones_pasadas = sesiones_totales.filter(inicio__lt=now).count()
    sesiones_futuras = sesiones_totales.filter(inicio__gte=now).count()
    sesiones_hoy = sesiones_totales.filter(inicio__date=now.date()).count()
    
    # Anotar estadísticas para cada sesión
    sesiones_con_stats = []
    for sesion in sesiones_qs:
        # Alumnos matriculados activamente en el horario
        alumnos_matriculados = sesion.horario.matriculas.filter(estado='activa').count()
        
        # Asistencias de la sesión
        asistencias_sesion = sesion.asistencias.filter(
            alumno__matriculas__horario=sesion.horario,
            alumno__matriculas__estado='activa'
        )
        total_asistencias = asistencias_sesion.count()
        asistencias_presentes = asistencias_sesion.filter(presente=True).count()
        asistencias_faltas = asistencias_sesion.filter(presente=False).count()
        
        # Porcentaje de asistencia
        porcentaje_asistencia = 0
        if total_asistencias > 0:
            porcentaje_asistencia = round((asistencias_presentes / total_asistencias) * 100, 1)
        
        # Estado de la sesión
        if sesion.inicio < now:
            estado_sesion = 'pasada'
        elif sesion.inicio.date() == now.date():
            estado_sesion = 'hoy'
        else:
            estado_sesion = 'futura'
        
        sesiones_con_stats.append({
            'sesion': sesion,
            'alumnos_matriculados': alumnos_matriculados,
            'total_asistencias': total_asistencias,
            'asistencias_presentes': asistencias_presentes,
            'asistencias_faltas': asistencias_faltas,
            'porcentaje_asistencia': porcentaje_asistencia,
            'estado_sesion': estado_sesion,
        })
    
    # Ordenar por fecha de inicio (más recientes primero)
    sesiones_con_stats.sort(key=lambda x: x['sesion'].inicio, reverse=True)
    
    # Obtener listas para filtros
    horarios = Horario.objects.filter(activo=True).order_by('asignatura')
    from .models import Profesor
    profesores = Profesor.objects.filter(activo=True).order_by('user__first_name', 'user__last_name')
    
    context = {
        'titulo': 'Gestión de Sesiones',
        'sesiones': sesiones_con_stats,
        'horarios': horarios,
        'profesores': profesores,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'total_sesiones': total_sesiones,
        'sesiones_pasadas': sesiones_pasadas,
        'sesiones_futuras': sesiones_futuras,
        'sesiones_hoy': sesiones_hoy,
        'filters': {
            'q': q,
            'horario': horario_id,
            'profesor': profesor_id,
            'estado': estado,
        }
    }
    return render(request, 'gestion/sesiones.html', context)

@login_required(login_url='login:login')
def reportes(request):
    """Generación de reportes"""
    context = {
        'titulo': 'Reportes',
    }
    return render(request, 'gestion/reportes.html', context)

@login_required(login_url='login:login')
def detalle_alumno(request, alumno_id):
    """Vista detallada de un alumno específico"""
    from .models import Alumno
    from django.db.models import Sum, Q
    from datetime import timedelta
    
    try:
        alumno = Alumno.objects.get(id=alumno_id)
    except Alumno.DoesNotExist:
        messages.error(request, 'Alumno no encontrado.')
        return redirect('gestion:alumnos')
    
    # Obtener mes y año actual
    now = timezone.now()
    mes_actual = now.month
    año_actual = now.year
    
    # Estadísticas generales
    horarios_matriculados = alumno.matriculas.filter(estado='activa')
    total_horarios = horarios_matriculados.count()
    
    # Asistencias del mes actual
    asistencias_mes = alumno.asistencias.filter(
        sesion__inicio__month=mes_actual,
        sesion__inicio__year=año_actual
    ).order_by('-sesion__inicio')
    
    asistencias_presente = asistencias_mes.filter(presente=True).count()
    asistencias_faltas = asistencias_mes.filter(presente=False).count()
    total_sesiones_mes = asistencias_mes.count()
    
    porcentaje_asistencia = 0
    if total_sesiones_mes > 0:
        porcentaje_asistencia = round((asistencias_presente / total_sesiones_mes) * 100, 1)
    
    # Historial de pagos
    pagos_alumno = alumno.pago_set.all().order_by('-fecha')
    total_pagado = pagos_alumno.aggregate(total=Sum('importe_final'))['total'] or 0
    pagos_mes_actual = pagos_alumno.filter(
        fecha__month=mes_actual,
        fecha__year=año_actual
    ).aggregate(total=Sum('importe_final'))['total'] or 0
    
    # Faltas de asistencia (últimos 3 meses)
    tres_meses_atras = now - timedelta(days=90)
    faltas_recientes = alumno.asistencias.filter(
        presente=False,
        sesion__inicio__gte=tres_meses_atras
    ).order_by('-sesion__inicio')
    
    # Próximas sesiones
    proximas_sesiones = []
    for matricula in horarios_matriculados:
        proxima = matricula.horario.sesiones.filter(
            inicio__gte=now
        ).order_by('inicio').first()
        if proxima:
            proximas_sesiones.append({
                'sesion': proxima,
                'horario': matricula.horario,
                'matricula': matricula
            })
    
    # Ordenar por fecha de sesión
    proximas_sesiones.sort(key=lambda x: x['sesion'].inicio)
    
    # Historial de asistencias (últimos 6 meses)
    seis_meses_atras = now - timedelta(days=180)
    historial_asistencias = alumno.asistencias.filter(
        sesion__inicio__gte=seis_meses_atras
    ).order_by('-sesion__inicio')
    
    context = {
        'titulo': f'Detalle de {alumno.nombre} {alumno.apellido}',
        'alumno': alumno,
        'total_horarios': total_horarios,
        'asistencias_presente': asistencias_presente,
        'asistencias_faltas': asistencias_faltas,
        'total_sesiones_mes': total_sesiones_mes,
        'porcentaje_asistencia': porcentaje_asistencia,
        'pagos_alumno': pagos_alumno,
        'total_pagado': total_pagado,
        'pagos_mes_actual': pagos_mes_actual,
        'faltas_recientes': faltas_recientes,
        'proximas_sesiones': proximas_sesiones,
        'historial_asistencias': historial_asistencias,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
    }
    
    return render(request, 'gestion/detalle_alumno.html', context)

@login_required(login_url='login:login')
def detalle_horario(request, horario_id):
    """Vista detallada de un horario específico"""
    from .models import Horario
    from django.db.models import Count, Sum, Q
    from datetime import timedelta
    
    try:
        horario = Horario.objects.get(id=horario_id)
    except Horario.DoesNotExist:
        messages.error(request, 'Horario no encontrado.')
        return redirect('gestion:horarios')
    
    # Obtener mes y año actual
    now = timezone.now()
    mes_actual = now.month
    año_actual = now.year
    
    # Estadísticas del horario
    matriculas_activas = horario.matriculas.filter(estado='activa')
    total_alumnos = matriculas_activas.count()
    
    # Ocupación del aula
    ocupacion = 0
    if horario.capacidad > 0:
        ocupacion = round((total_alumnos / horario.capacidad) * 100, 1)
    
    # Sesiones del mes actual
    sesiones_mes = horario.sesiones.filter(
        inicio__month=mes_actual,
        inicio__year=año_actual
    ).order_by('-inicio')
    
    total_sesiones_mes = sesiones_mes.count()
    
    # Asistencias del mes
    asistencias_mes = horario.sesiones.filter(
        inicio__month=mes_actual,
        inicio__year=año_actual
    ).aggregate(
        total_asistencias=Count('asistencias__id', filter=Q(asistencias__presente=True))
    )['total_asistencias'] or 0
    
    # Próximas sesiones
    proximas_sesiones = horario.sesiones.filter(
        inicio__gte=now
    ).order_by('inicio')[:5]  # Próximas 5 sesiones
    
    # Últimas sesiones con estadísticas
    ultimas_sesiones_raw = horario.sesiones.filter(
        inicio__lt=now
    ).order_by('-inicio')[:5]  # Últimas 5 sesiones
    
    ultimas_sesiones = []
    for sesion in ultimas_sesiones_raw:
        # Solo contar asistencias de alumnos matriculados activamente en este horario
        alumnos_matriculados_ids = list(matriculas_activas.values_list('alumno_id', flat=True))
        
        asistencias_sesion = sesion.asistencias.filter(alumno_id__in=alumnos_matriculados_ids)
        total_asistencias = asistencias_sesion.count()
        asistencias_presentes = asistencias_sesion.filter(presente=True).count()
        asistencias_faltas = asistencias_sesion.filter(presente=False).count()
        
        porcentaje_asistencia = 0
        if total_asistencias > 0:
            porcentaje_asistencia = round((asistencias_presentes / total_asistencias) * 100, 1)
        
        ultimas_sesiones.append({
            'sesion': sesion,
            'total_asistencias': total_asistencias,
            'asistencias_presentes': asistencias_presentes,
            'asistencias_faltas': asistencias_faltas,
            'porcentaje_asistencia': porcentaje_asistencia,
        })
    
    # Alumnos matriculados con información adicional
    alumnos_matriculados = []
    for matricula in matriculas_activas:
        # Asistencias del alumno este mes
        asistencias_alumno = matricula.alumno.asistencias.filter(
            sesion__horario=horario,
            sesion__inicio__month=mes_actual,
            sesion__inicio__year=año_actual
        )
        
        total_asistencias_alumno = asistencias_alumno.count()
        asistencias_presente_alumno = asistencias_alumno.filter(presente=True).count()
        
        porcentaje_asistencia = 0
        if total_asistencias_alumno > 0:
            porcentaje_asistencia = round((asistencias_presente_alumno / total_asistencias_alumno) * 100, 1)
        
        # Última asistencia
        ultima_asistencia = matricula.alumno.asistencias.filter(
            sesion__horario=horario
        ).order_by('-sesion__inicio').first()
        
        alumnos_matriculados.append({
            'matricula': matricula,
            'alumno': matricula.alumno,
            'asistencias_este_mes': asistencias_presente_alumno,
            'total_sesiones_mes': total_asistencias_alumno,
            'porcentaje_asistencia': porcentaje_asistencia,
            'ultima_asistencia': ultima_asistencia,
        })
    
    # Ordenar alumnos por apellido
    alumnos_matriculados.sort(key=lambda x: (x['alumno'].apellido, x['alumno'].nombre))
    
    # Estadísticas de asistencia general - cálculo más preciso
    total_asistencias_posibles = 0
    total_asistencias_presentes = 0
    
    # Solo contar asistencias de alumnos matriculados activamente
    alumnos_matriculados_ids = list(matriculas_activas.values_list('alumno_id', flat=True))
    
    for sesion in sesiones_mes:
        asistencias_sesion = sesion.asistencias.filter(alumno_id__in=alumnos_matriculados_ids).count()
        asistencias_presentes_sesion = sesion.asistencias.filter(
            alumno_id__in=alumnos_matriculados_ids, 
            presente=True
        ).count()
        total_asistencias_posibles += asistencias_sesion
        total_asistencias_presentes += asistencias_presentes_sesion
    
    porcentaje_asistencia_general = 0
    if total_asistencias_posibles > 0:
        porcentaje_asistencia_general = round((total_asistencias_presentes / total_asistencias_posibles) * 100, 1)
    
    # Actualizar asistencias_mes para que coincida con el cálculo
    asistencias_mes = total_asistencias_presentes
    
    context = {
        'titulo': f'Detalle de {horario.asignatura}',
        'horario': horario,
        'total_alumnos': total_alumnos,
        'ocupacion': ocupacion,
        'sesiones_mes': sesiones_mes,
        'total_sesiones_mes': total_sesiones_mes,
        'asistencias_mes': asistencias_mes,
        'proximas_sesiones': proximas_sesiones,
        'ultimas_sesiones': ultimas_sesiones,
        'alumnos_matriculados': alumnos_matriculados,
        'porcentaje_asistencia_general': porcentaje_asistencia_general,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
    }
    
    return render(request, 'gestion/detalle_horario.html', context)

@login_required(login_url='login:login')
def detalle_asistencias(request, sesion_id):
    """Vista detallada de asistencias de una sesión específica"""
    from .models import Sesion
    from django.db.models import Q
    
    try:
        sesion = Sesion.objects.get(id=sesion_id)
    except Sesion.DoesNotExist:
        messages.error(request, 'Sesión no encontrada.')
        return redirect('gestion:horarios')
    
    # Obtener alumnos matriculados activamente en el horario
    matriculas_activas = sesion.horario.matriculas.filter(estado='activa')
    alumnos_matriculados_ids = list(matriculas_activas.values_list('alumno_id', flat=True))
    
    # Obtener todas las asistencias de la sesión
    asistencias_sesion = sesion.asistencias.all()
    
    # Separar asistencias por estado
    asistencias_presentes = []
    asistencias_faltas = []
    asistencias_otros = []
    
    for asistencia in asistencias_sesion:
        if asistencia.alumno_id in alumnos_matriculados_ids:
            # Alumno matriculado activamente
            if asistencia.presente:
                asistencias_presentes.append(asistencia)
            else:
                asistencias_faltas.append(asistencia)
        else:
            # Alumno no matriculado o inactivo
            asistencias_otros.append(asistencia)
    
    # Estadísticas
    total_matriculados = len(alumnos_matriculados_ids)
    total_presentes = len(asistencias_presentes)
    total_faltas = len(asistencias_faltas)
    total_otros = len(asistencias_otros)
    
    porcentaje_asistencia = 0
    if total_matriculados > 0:
        porcentaje_asistencia = round((total_presentes / total_matriculados) * 100, 1)
    
    # Alumnos matriculados que no tienen registro de asistencia
    alumnos_sin_registro = []
    for matricula in matriculas_activas:
        if not sesion.asistencias.filter(alumno=matricula.alumno).exists():
            alumnos_sin_registro.append(matricula.alumno)
    
    context = {
        'titulo': f'Asistencias - {sesion.horario.asignatura}',
        'sesion': sesion,
        'asistencias_presentes': asistencias_presentes,
        'asistencias_faltas': asistencias_faltas,
        'asistencias_otros': asistencias_otros,
        'alumnos_sin_registro': alumnos_sin_registro,
        'total_matriculados': total_matriculados,
        'total_presentes': total_presentes,
        'total_faltas': total_faltas,
        'total_otros': total_otros,
        'porcentaje_asistencia': porcentaje_asistencia,
    }
    
    return render(request, 'gestion/detalle_asistencias.html', context)

@login_required(login_url='login:login')
def gastos(request):
    """Gestión de gastos con estadísticas completas"""
    now = timezone.now()
    mes_actual = now.month
    año_actual = now.year
    
    # Filters GET
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    gastos_qs = Gasto.objects.all()
    
    # Apply filters
    if q:
        gastos_qs = gastos_qs.filter(
            Q(concepto__icontains=q) |
            Q(observaciones__icontains=q)
        )
    
    if categoria:
        gastos_qs = gastos_qs.filter(categoria=categoria)
    
    if fecha_desde:
        try:
            fecha_desde_parsed = parse_date(fecha_desde)
            gastos_qs = gastos_qs.filter(fecha_gasto__gte=fecha_desde_parsed)
        except:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_parsed = parse_date(fecha_hasta)
            gastos_qs = gastos_qs.filter(fecha_gasto__lte=fecha_hasta_parsed)
        except:
            pass
    
    # Statistics
    total_gastos = gastos_qs.aggregate(total=Sum('importe'))['total'] or 0
    gastos_mes = gastos_qs.filter(fecha_gasto__month=mes_actual, fecha_gasto__year=año_actual).aggregate(total=Sum('importe'))['total'] or 0
    
    # Gastos por categoría
    gastos_por_categoria = gastos_qs.values('categoria').annotate(
        total=Sum('importe'),
        count=Count('id')
    ).order_by('-total')
    
    # Gastos del mes actual
    gastos_mes_actual = gastos_qs.filter(
        fecha_gasto__month=mes_actual, 
        fecha_gasto__year=año_actual
    ).order_by('-fecha_gasto')
    
    context = {
        'titulo': 'Gestión de Gastos',
        'gastos': gastos_qs.order_by('-fecha_gasto'),
        'total_gastos': total_gastos,
        'gastos_mes': gastos_mes,
        'gastos_por_categoria': gastos_por_categoria,
        'gastos_mes_actual': gastos_mes_actual,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'categorias': Gasto.CATEGORIAS_GASTO,
        'filters': {
            'q': q,
            'categoria': categoria,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    return render(request, 'gestion/gastos.html', context)


