"""
URL configuration for ProyectoWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Personalizar el admin de Django
admin.site.site_header = "Sistema de Gestión Académica"
admin.site.site_title = "Admin - Gestión Académica"
admin.site.index_title = "Panel de Administración"

# Personalizar el botón "VER EL SITIO" para que redirija al sistema de gestión
class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Modificar el enlace del sitio para que apunte al sistema de gestión
        for app in app_list:
            if app['app_label'] == 'gestion':
                app['has_module_perms'] = True
        return app_list

# Crear una vista personalizada para el botón "VER EL SITIO"
def redirect_to_gestion(request):
    return redirect('gestion:inicio')

# Registrar la vista personalizada
admin.site.site_url = '/gestion/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('proyectoWebApp.urls')),
    path('servicios/', include('servicios.urls')),
    path('blog/', include('blog.urls')),
    path('contacto/', include('contacto.urls')),
    path('login/', include('login.urls')),
    path('gestion/', include('gestion.urls')),
    path('instalaciones/', include('instalaciones.urls')),
    path('tienda/', include('tienda.urls')),
    path('reportes/', include('reportes.urls')),
]
