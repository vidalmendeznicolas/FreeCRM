from tabnanny import verbose
from tkinter import image_names
from django.db import models

# Create your models here.

class Servicio(models.Model):
    titulo=models.CharField(max_length=50)
    contenido=models.CharField(max_length=50)
    imagen=models.ImageField(upload_to='servicios')
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)

    # Nombre que tendrá este servicio en la BBDD
    class Meta:
        verbose_name='servicio'
        verbose_name_plural='servicios'

    def __str__(self):
            return self.titulo