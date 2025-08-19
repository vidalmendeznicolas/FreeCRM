from django.shortcuts import render
from servicios.models import Servicio
from instalaciones.models import Instalacion

# Create your views here.

def home(request):
    servicios = Servicio.objects.all()[:3]  # Máximo 3 servicios
    instalaciones = Instalacion.objects.all()[:3]  # Máximo 3 instalaciones
    return render(request, "proyectoWebApp/home.html", {
        'servicios': servicios,
        'instalaciones': instalaciones
    })


