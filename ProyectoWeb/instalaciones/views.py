from django.shortcuts import render
from instalaciones.models import Instalacion
# Create your views here.

    
def instalaciones(request):
    instalaciones = Instalacion.objects.all()
    return render(request, "instalaciones/instalaciones.html", {'instalaciones': instalaciones})
