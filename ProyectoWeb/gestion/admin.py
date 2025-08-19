from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe
import io
from xhtml2pdf import pisa

from .models import Alumno, Profesor, Padres, Horario, MatriculaHorario, Sesion, Asistencia, Pago, Tarifa, Gasto


class PagoAdminForm(forms.ModelForm):
    generar_comprobante = forms.BooleanField(
        label='Generar comprobante PDF',
        required=False,
        initial=True,
        help_text='Marcar esta casilla para generar automáticamente el comprobante de pago en PDF'
    )
    
    class Meta:
        model = Pago
        fields = '__all__'


class MatriculaHorarioInline(admin.TabularInline):
    model = MatriculaHorario
    extra = 0
    autocomplete_fields = ['horario', 'alumno']


class HorarioInline(admin.TabularInline):
    model = Horario
    extra = 0


class SesionInline(admin.TabularInline):
    model = Sesion
    extra = 0


class AsistenciaInline(admin.TabularInline):
    model = Asistencia
    extra = 0
    autocomplete_fields = ['alumno']
    fields = ['alumno', 'presente']  # Especificar los campos a mostrar


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'curso', 'telefono', 'es_compartido', 'tarifa_predeterminada', 'activo', 'fecha_alta')
    list_filter = ('activo', 'es_compartido', 'curso', 'fecha_alta', 'tarifa_predeterminada')
    search_fields = ('nombre', 'apellido', 'dni', 'telefono')
    autocomplete_fields = ['padre', 'tarifa_predeterminada']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'dni', 'curso', 'telefono', 'fecha_nacimiento')
        }),
        ('Información Adicional', {
            'fields': ('direccion', 'observaciones', 'padre')
        }),
        ('Configuración', {
            'fields': ('activo', 'es_compartido', 'tarifa_predeterminada')
        }),
        ('Fechas', {
            'fields': ('fecha_alta', 'fecha_baja'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('fecha_alta',)
    inlines = [MatriculaHorarioInline]
    
    def response_change(self, request, obj):
        """Redirigir después de editar"""
        if '_redirect' in request.GET:
            return redirect(request.GET['_redirect'])
        return super().response_change(request, obj)
    
    def response_add(self, request, obj):
        """Redirigir después de añadir"""
        if '_redirect' in request.GET:
            return redirect(request.GET['_redirect'])
        return super().response_add(request, obj)


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'activo', 'fecha_alta')
    list_filter = ('activo', 'fecha_alta')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'telefono')
    inlines = [HorarioInline]


@admin.register(Padres)
class PadresAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'telefono')
    search_fields = ('nombre', 'apellido', 'telefono')


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ('asignatura', 'profesor', 'dia_semana', 'hora_inicio', 'hora_fin', 'aula', 'capacidad', 'activo', 'crear_sesion_link')
    list_filter = ('dia_semana', 'activo', 'profesor')
    search_fields = ('asignatura', 'aula', 'profesor__user__first_name', 'profesor__user__last_name')
    inlines = [MatriculaHorarioInline, SesionInline]
    
    def response_change(self, request, obj):
        """Redirigir después de editar"""
        if '_redirect' in request.GET:
            return redirect(request.GET['_redirect'])
        return super().response_change(request, obj)
    
    def response_add(self, request, obj):
        """Redirigir después de añadir"""
        if '_redirect' in request.GET:
            return redirect(request.GET['_redirect'])
        return super().response_add(request, obj)
    
    def crear_sesion_link(self, obj):
        if obj.activo:
            return format_html('<a href="/admin/gestion/sesion/add/?horario={}" class="btn btn-sm btn-success">📅 Crear Sesión</a>', obj.id)
        return '-'
    crear_sesion_link.short_description = 'Acciones'
    crear_sesion_link.allow_tags = True


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activa', 'fecha_creacion', 'fecha_actualizacion')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('nombre', 'observaciones')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ['nombre']
    
    def get_search_results(self, request, queryset, search_term):
        """Personalizar búsqueda para autocompletado"""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = queryset.filter(activa=True)
        return queryset, use_distinct

@admin.register(MatriculaHorario)
class MatriculaHorarioAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'horario', 'fecha_matricula', 'estado')
    list_filter = ('estado', 'fecha_matricula', 'horario__profesor')
    search_fields = ('alumno__nombre', 'alumno__apellido', 'horario__asignatura')
    autocomplete_fields = ['alumno', 'horario']


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ('horario', 'inicio', 'fin')
    list_filter = ('horario__profesor',)
    date_hierarchy = 'inicio'
    search_fields = ('horario__asignatura', 'horario__profesor__user__first_name', 'horario__profesor__user__last_name')
    inlines = [AsistenciaInline]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Si es una nueva sesión, pre-llenar con datos del horario
        if obj is None:  # Nueva sesión
            horario_id = request.GET.get('horario')
            if horario_id:
                try:
                    from .models import Horario
                    from datetime import datetime, date
                    
                    horario = Horario.objects.get(id=horario_id)
                    
                    # Obtener la fecha actual
                    today = date.today()
                    
                    # Crear datetime completo con la fecha actual y las horas del horario
                    inicio_datetime = datetime.combine(today, horario.hora_inicio)
                    fin_datetime = datetime.combine(today, horario.hora_fin)
                    
                    # Usar timezone naive datetime para evitar problemas
                    # Django se encargará de la conversión de timezone
                    
                    # Pre-llenar los campos
                    form.base_fields['inicio'].initial = inicio_datetime
                    form.base_fields['fin'].initial = fin_datetime
                    
                except Horario.DoesNotExist:
                    pass
        
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Si es una nueva sesión, crear automáticamente asistencias para todos los alumnos matriculados
        if not change:  # Solo para nuevas sesiones
            from .models import Asistencia
            # Obtener todos los alumnos matriculados en este horario
            alumnos_matriculados = obj.horario.matriculas.filter(estado='activa').select_related('alumno')
            
            # Crear registros de asistencia para cada alumno
            asistencias_a_crear = []
            for matricula in alumnos_matriculados:
                asistencias_a_crear.append(Asistencia(
                    sesion=obj,
                    alumno=matricula.alumno,
                    presente=False  # Por defecto no presente
                ))
            
            # Crear todas las asistencias de una vez
            if asistencias_a_crear:
                Asistencia.objects.bulk_create(asistencias_a_crear, ignore_conflicts=True)


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('sesion', 'alumno', 'presente')
    list_filter = ('presente', 'sesion__horario__profesor')
    search_fields = ('alumno__nombre', 'alumno__apellido', 'sesion__horario__asignatura')
    autocomplete_fields = ['sesion', 'alumno']



@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    form = PagoAdminForm
    list_display = ('numero', 'alumno', 'tarifa', 'importe_original', 'descuento', 'importe_final', 'fecha', 'comprobante_link')
    list_filter = ('fecha', 'tarifa', 'profesor')
    search_fields = ('numero', 'alumno__nombre', 'alumno__apellido', 'concepto')
    readonly_fields = ('comprobante', 'fecha')
    autocomplete_fields = ['alumno', 'profesor']
    fieldsets = (
        ('Información General', {
            'fields': ('numero', 'alumno', 'profesor', 'concepto')
        }),
        ('Tarifa y Descuentos', {
            'fields': ('tarifa', 'importe_original', 'descuento', 'importe_final')
        }),
        ('Documentación', {
            'fields': ('comprobante', 'generar_comprobante')
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Configurar el campo importe_original para auto-relleno
        if 'importe_original' in form.base_fields:
            form.base_fields['importe_original'].widget.attrs.update({
                'class': 'form-control auto-fill-field',
                'placeholder': 'Se rellena automáticamente al seleccionar tarifa'
            })
        
        # Configurar el campo importe_final para cálculos automáticos
        if 'importe_final' in form.base_fields:
            form.base_fields['importe_final'].widget.attrs.update({
                'class': 'form-control calculated-field',
                'placeholder': 'Se calcula automáticamente'
            })
        
        # Pre-llenar tarifa si se selecciona un alumno con tarifa predeterminada
        if 'alumno' in form.base_fields and 'tarifa' in form.base_fields:
            form.base_fields['alumno'].widget.attrs.update({
                'onchange': 'prefillTarifa(this.value)'
            })
        
        # Pre-llenar numero con el siguiente correlativo si es nuevo
        if obj is None and 'numero' in form.base_fields:
            try:
                form.base_fields['numero'].initial = Pago.generar_siguiente_numero()
            except Exception:
                pass
        
        return form
    
    def response_change(self, request, obj):
        """Redirigir después de editar"""
        if '_redirect' in request.GET:
            return redirect(request.GET['_redirect'])
        return super().response_change(request, obj)
    
    def response_add(self, request, obj):
        """Redirigir después de añadir"""
        if '_redirect' in request.GET:
            return redirect(request.GET['_redirect'])
        return super().response_add(request, obj)

    def save_model(self, request, obj, form, change):
        # Obtener el valor del checkbox antes de guardar
        generar_comprobante = form.cleaned_data.get('generar_comprobante', False)
        
        # Autogenerar numero si viene vacío por cualquier motivo
        if not getattr(obj, 'numero', None):
            try:
                obj.numero = Pago.generar_siguiente_numero()
            except Exception:
                pass
        
        # Guardar el modelo primero
        super().save_model(request, obj, form, change)
        
        # Generar comprobante solo si está marcado el checkbox
        if generar_comprobante and not obj.comprobante:
            html = render_to_string('gestion/pagos/comprobante.html', {'pago': obj})
            pdf_io = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=pdf_io, encoding='utf-8')
            obj.comprobante.save(f'comprobante_{obj.numero}.pdf', ContentFile(pdf_io.getvalue()), save=True)

    def comprobante_link(self, obj):
        if obj.comprobante:
            return format_html('<a href="{}" target="_blank" class="btn btn-sm btn-primary">📄 Descargar PDF</a>', obj.comprobante.url)
        return '-'
    comprobante_link.allow_tags = True
    comprobante_link.short_description = 'Comprobante'


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('concepto', 'importe', 'categoria', 'fecha_gasto', 'fecha', 'factura_link')
    list_filter = ('categoria', 'fecha_gasto', 'fecha')
    search_fields = ('concepto', 'observaciones')
    readonly_fields = ('fecha',)
    fieldsets = (
        ('Información General', {
            'fields': ('concepto', 'importe', 'categoria', 'fecha_gasto')
        }),
        ('Detalles', {
            'fields': ('observaciones', 'factura')
        }),
    )
    
    def factura_link(self, obj):
        if obj.factura:
            filename = obj.get_factura_filename()
            return format_html(
                '<a href="{}" target="_blank" class="btn btn-sm btn-primary">📄 {}</a>', 
                obj.factura.url, 
                filename[:20] + '...' if len(filename) > 20 else filename
            )
        return '-'
    factura_link.allow_tags = True
    factura_link.short_description = 'Factura'