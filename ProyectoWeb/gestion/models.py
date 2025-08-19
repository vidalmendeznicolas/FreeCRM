from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os
import re

class Alumno(models.Model):
    CURSOS_CHOICES = [
        # Primaria
        ('1P', '1º Primaria'),
        ('2P', '2º Primaria'),
        ('3P', '3º Primaria'),
        ('4P', '4º Primaria'),
        ('5P', '5º Primaria'),
        ('6P', '6º Primaria'),
        # ESO
        ('1E', '1º E.S.O'),
        ('2E', '2º E.S.O'),
        ('3E', '3º E.S.O'),
        ('4E', '4º E.S.O'),
        # Bachillerato
        ('1B', '1º Bachillerato'),
        ('2B', '2º Bachillerato'),
        # Otros
        ('FP', 'FP'),
        ('AD', 'Adultos'),
        ('EB', 'EBAU'),
        ('EO', 'EOI'),
    ]
    
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    dni = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="DNI del alumno (opcional)")
    curso = models.CharField(max_length=2, choices=CURSOS_CHOICES, blank=True, help_text="Curso en el que está matriculado el alumno")
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    es_compartido = models.BooleanField(default=False, help_text="Indica si este alumno puede ser compartido entre profesores en el mismo horario")
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(null=True, blank=True)
    padre = models.ForeignKey('Padres', on_delete=models.SET_NULL, null=True, blank=True, related_name='hijos')
    tarifa_predeterminada = models.ForeignKey('Tarifa', on_delete=models.SET_NULL, null=True, blank=True, 
                                            help_text="Tarifa predeterminada para este alumno")

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_profesor')
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Padres(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

DIAS_SEMANA = [
    (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
    (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
]

class Horario(models.Model):
    profesor = models.ForeignKey('Profesor', on_delete=models.PROTECT, related_name='horarios')
    asignatura = models.CharField(max_length=100)
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=50, blank=True)
    capacidad = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.asignatura} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin} ({self.profesor})"

class MatriculaHorario(models.Model):
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE, related_name='matriculas')
    horario = models.ForeignKey('Horario', on_delete=models.CASCADE, related_name='matriculas')
    fecha_matricula = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='activa', choices=[
        ('activa', 'Activa'), ('baja', 'Baja'), ('pendiente', 'Pendiente')
    ])
    notas = models.TextField(blank=True)

    class Meta:
        unique_together = [('alumno', 'horario')]  # evita duplicados

    def __str__(self):
        return f"{self.alumno} -> {self.horario}"

class Sesion(models.Model):
    horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='sesiones')
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    
    def __str__(self):
        return f"{self.horario.asignatura} - {self.inicio.strftime('%d/%m/%Y %H:%M')}"

class Asistencia(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name='asistencias')
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE, related_name='asistencias')
    presente = models.BooleanField(default=False)

    class Meta:
        unique_together = [('sesion', 'alumno')]
        
    def __str__(self):
        return f"{self.alumno.nombre} {self.alumno.apellido}"
        
class Tarifa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio en euros")
    observaciones = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_baja = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.precio}€"
    
    class Meta:
        verbose_name = "Tarifa"
        verbose_name_plural = "Tarifas"
        ordering = ['nombre']

class Pago(models.Model):
    alumno = models.ForeignKey('Alumno', on_delete=models.PROTECT)
    profesor = models.ForeignKey('Profesor', on_delete=models.PROTECT, blank=True, null=True)
    tarifa = models.ForeignKey('Tarifa', on_delete=models.PROTECT, null=True, blank=True)
    numero = models.CharField(max_length=20, unique=True)
    fecha = models.DateField(auto_now_add=True)
    importe_original = models.DecimalField(max_digits=10, decimal_places=2, help_text="Importe original de la tarifa", default=0)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Descuento aplicado en euros")
    importe_final = models.DecimalField(max_digits=10, decimal_places=2, help_text="Importe final después del descuento", default=0)
    concepto = models.CharField(max_length=200, blank=True)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    
    @staticmethod
    def generar_siguiente_numero() -> str:
        from datetime import datetime
        year = datetime.now().year
        prefix = f"PG-{year}-"
        
        # Buscar el último pago del año actual
        ultimo = Pago.objects.filter(numero__startswith=prefix).order_by('-numero').first()
        
        if not ultimo:
            # Primer pago del año
            return f"{prefix}0001"
        
        # Extraer el número del último pago
        try:
            # Obtener la parte numérica después del prefijo
            numero_str = ultimo.numero.replace(prefix, "")
            numero_actual = int(numero_str)
            numero_siguiente = numero_actual + 1
            return f"{prefix}{numero_siguiente:04d}"
        except (ValueError, AttributeError):
            # Fallback: usar el ID + 1
            ultimo_por_id = Pago.objects.order_by('-id').first()
            if ultimo_por_id:
                return f"{prefix}{(ultimo_por_id.id + 1):04d}"
            return f"{prefix}0001"
    
    def save(self, *args, **kwargs):
        # Calcular importe final automáticamente
        if self.importe_original is not None and self.descuento is not None:
            self.importe_final = self.importe_original - self.descuento
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pago {self.numero} - {self.alumno} - {self.importe_final}€"

def gasto_factura_path(instance, filename):
    """Genera una ruta organizada para las facturas de gastos"""
    # Obtener la extensión del archivo
    ext = filename.split('.')[-1]
    # Crear nombre de archivo: gasto_id_fecha.ext
    new_filename = f"gasto_{instance.id}_{instance.fecha_gasto.strftime('%Y%m%d')}.{ext}"
    # Ruta organizada por año/mes/categoría
    return f'gastos/{instance.fecha_gasto.year}/{instance.fecha_gasto.month:02d}/{instance.categoria}/{new_filename}'

class Gasto(models.Model):
    CATEGORIAS_GASTO = [
        ('suministros', 'Suministros'),
        ('inmobiliario', 'Inmobiliario'),
        ('equipamiento', 'Equipamiento'),
        ('limpieza', 'Limpieza'),
        ('marketing', 'Marketing'),
        ('administrativo', 'Administrativo'),
        ('otros', 'Otros'),
    ]
    
    concepto = models.CharField(max_length=200, help_text="Descripción del gasto")
    importe = models.DecimalField(max_digits=10, decimal_places=2, help_text="Importe en euros")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_GASTO, default='otros')
    observaciones = models.TextField(blank=True, help_text="Observaciones adicionales")
    fecha = models.DateField(auto_now_add=True)
    fecha_gasto = models.DateField(help_text="Fecha en que se realizó el gasto")
    factura = models.FileField(
        upload_to=gasto_factura_path,
        blank=True, 
        null=True, 
        help_text="Factura o comprobante del gasto (PDF, JPG, PNG)",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'],
                message="Solo se permiten archivos PDF, JPG o PNG."
            )
        ]
    )
    
    def __str__(self):
        return f"{self.concepto} - {self.importe}€ ({self.get_categoria_display()})"
    
    def get_factura_filename(self):
        """Obtiene el nombre del archivo de la factura"""
        if self.factura:
            return os.path.basename(self.factura.name)
        return None
    
    def has_factura(self):
        """Verifica si tiene factura adjunta"""
        return bool(self.factura)
    
    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ['-fecha_gasto', '-fecha']