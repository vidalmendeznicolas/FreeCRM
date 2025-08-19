# 🎓 Sistema de Gestión Académica

Un sistema completo de gestión para centros educativos desarrollado en Django, que permite administrar alumnos, profesores, horarios, pagos, asistencias y generar reportes detallados.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Funcionalidades](#-funcionalidades)
- [Uso del Sistema](#-uso-del-sistema)
- [Contribución](#-contribución)

## ✨ Características

### 🏠 Sitio Web Público
- **Página de inicio** moderna con diseño responsive
- **Sección de servicios** con información detallada
- **Blog** con categorías y artículos
- **Página de contacto** con formulario funcional
- **Galería de instalaciones** con imágenes
- **Tienda online** integrada

### 🔐 Sistema de Autenticación
- **Login seguro** con Django Authentication
- **Dashboard personalizado** para usuarios autenticados
- **Sistema de logout** con redirección automática
- **Protección de rutas** con decoradores de login

### 👥 Gestión de Alumnos
- **Registro completo** de información personal
- **Cursos académicos** (Primaria, ESO, Bachillerato, FP, etc.)
- **Sistema de matrículas** por horarios
- **Alumnos compartidos** entre profesores
- **Estado activo/inactivo** con fechas de alta/baja
- **Filtros avanzados** por curso, estado, compartidos
- **Vista detallada** con historial completo

### 👨‍🏫 Gestión de Profesores
- **Perfiles completos** con información de contacto
- **Asignación a horarios** específicos
- **Gestión de clases** y sesiones
- **Control de asistencias** de alumnos

### 📅 Gestión de Horarios
- **Creación de horarios** por asignatura y profesor
- **Sistema de días** y horas configurable
- **Capacidad de aulas** configurable
- **Matrículas por horario** con estados
- **Vista de ocupación** y estadísticas

### 💰 Sistema de Pagos
- **Registro de pagos** con importes y descuentos
- **Tarifas configurables** por tipo de servicio
- **Números de pago automáticos** (formato PG-YYYY-NNNN)
- **Generación opcional de comprobantes** PDF
- **Historial completo** de pagos por alumno
- **Cálculo automático** de importes finales

### 📊 Control de Asistencias
- **Registro de sesiones** por horario
- **Asistencias automáticas** al crear sesiones
- **Marcado de presencia** individual
- **Estadísticas de asistencia** por alumno/horario
- **Vista de ausencias** y tendencias

### 💸 Gestión de Gastos
- **Registro de gastos** empresariales
- **Categorización** (suministros, inmobiliario, etc.)
- **Subida de facturas** (PDF, JPG, PNG)
- **Control de fechas** y observaciones
- **Organización por carpetas** automática

### 📈 Sistema de Reportes
- **Exportación a Excel** de todos los datos
- **Filtros avanzados** por fechas, categorías, etc.
- **Múltiples formatos** de reporte
- **Estadísticas en tiempo real**
- **Pestañas organizadas** en Excel

## 🛠 Tecnologías Utilizadas

- **Backend**: Django 5.2.4
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Iconos**: Font Awesome
- **PDF**: xhtml2pdf
- **Excel**: openpyxl
- **Imágenes**: Pillow
- **Validación**: Django Forms y Validators

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <https://github.com/vidalmendeznicolas/FreeCRM.git>
   cd FreeCRM
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual**
   
   **Windows:**
   ```bash
   .\venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Instalar dependencias principales**
   ```bash
   pip install django djangorestframework psycopg2-binary django-cors-headers
   ```

5. **Instalar librerías adicionales**
   ```bash
   pip install Pillow
   pip install xhtml2pdf
   pip install openpyxl
   ```

6. **Navegar al directorio del proyecto**
   ```bash
   cd ProyectoWeb
   ```

7. **Aplicar migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

8. **Crear superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

9. **Levantar el servidor**
   ```bash
   python manage.py runserver
   ```

10. **Acceder al sistema**
    - **Sitio público**: http://127.0.0.1:8000/
    - **Admin Django**: http://127.0.0.1:8000/admin/
    - **Sistema de gestión**: http://127.0.0.1:8000/gestion/

## 📁 Estructura del Proyecto

```
FreeCRM/
├── ProyectoWeb/
│   ├── ProyectoWeb/          # Configuración principal
│   │   ├── settings.py       # Configuración del proyecto
│   │   ├── urls.py          # URLs principales
│   │   └── wsgi.py          # Configuración WSGI
│   ├── proyectoWebApp/       # Aplicación principal (sitio público)
│   ├── gestion/             # Sistema de gestión académica
│   ├── login/               # Sistema de autenticación
│   ├── servicios/           # Gestión de servicios
│   ├── blog/                # Sistema de blog
│   ├── contacto/            # Formulario de contacto
│   ├── instalaciones/       # Galería de instalaciones
│   ├── tienda/              # Tienda online
│   ├── reportes/            # Sistema de reportes
│   ├── media/               # Archivos subidos
│   ├── static/              # Archivos estáticos
│   └── manage.py            # Script de gestión Django
└── venv/                    # Entorno virtual
```

## 🎯 Funcionalidades Detalladas

### Sitio Web Público
- **Diseño responsive** adaptado a móviles y tablets
- **Navegación moderna** con efectos visuales
- **Formulario de contacto** con validación
- **Blog categorizado** con sistema de comentarios
- **Galería de instalaciones** con imágenes optimizadas

### Panel de Administración
- **Interfaz personalizada** con colores corporativos
- **Gestión completa** de todos los modelos
- **Filtros avanzados** y búsquedas
- **Acciones en lote** para operaciones masivas
- **Validaciones automáticas** de datos

### Sistema de Gestión
- **Dashboard principal** con estadísticas en tiempo real
- **Gestión de alumnos** con filtros por curso y estado
- **Control de pagos** con generación automática de números
- **Gestión de horarios** con sistema de matrículas
- **Control de asistencias** con estadísticas detalladas
- **Gestión de gastos** con subida de facturas

### Reportes y Exportación
- **Exportación a Excel** con formato profesional
- **Filtros por fechas** y categorías
- **Múltiples pestañas** en archivos Excel
- **Estadísticas automáticas** y gráficos
- **Nombres de archivo** con timestamp

## 🔧 Configuración Avanzada

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
```

### Configuración de Email
En `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-password'
DEFAULT_FROM_EMAIL = 'Centro Educativo <tu-email@gmail.com>'
```

### Base de Datos PostgreSQL
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nombre_db',
        'USER': 'usuario_db',
        'PASSWORD': 'password_db',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📱 Uso del Sistema

### Acceso Inicial
1. Crear superusuario: `python manage.py createsuperuser`
2. Acceder a admin: http://127.0.0.1:8000/admin/
3. Configurar datos iniciales (tarifas, profesores, etc.)

### Flujo de Trabajo Típico
1. **Registrar profesores** en el sistema
2. **Registrar alumnos** en el sistema
3. **Crear horarios** y asignar profesores
4. **Matricular alumnos** en horarios específicos
5. **Crear sesiones** para cada horario
6. **Registrar asistencias** de los alumnos
7. **Gestionar pagos** con comprobantes
8. **Generar reportes** para análisis

### Funcionalidades Especiales
- **Alumnos compartidos**: Permite que un alumno sea atendido por diferentes profesores
- **Números automáticos**: Los pagos se numeran automáticamente (PG-2025-0001)
- **Comprobantes opcionales**: Checkbox para generar o no PDF de pago
- **Exportación inteligente**: Filtros y ordenación en reportes Excel

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Email: vidalmendeznicolas@gmail.com

## 🔄 Actualizaciones

### Versión 1.0.0
- Sistema base de gestión académica
- Sitio web público completo
- Panel de administración personalizado
- Sistema de reportes y exportación

---

**Desarrollado con ❤️ para centros educativos**