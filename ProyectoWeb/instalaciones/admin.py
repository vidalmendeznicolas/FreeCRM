from django.contrib import admin
from .models import Instalacion
# Register your models here.

# Para que aparezcan los campos de created y updated en admin
class InstalacionAdmin(admin.ModelAdmin):
    readonly_fields=('created','updated')

admin.site.register(Instalacion, InstalacionAdmin)