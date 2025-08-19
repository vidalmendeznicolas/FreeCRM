from django.contrib import admin
from .models import CategoriaProd, Producto
# Register your models here.
# Para que aparezcan los campos de created y updated en admin
class CategoriaProdAdmin(admin.ModelAdmin):
    readonly_fields=('created','updated')

class ProductoAdmin(admin.ModelAdmin):
    readonly_fields=('created','updated')

admin.site.register(CategoriaProd, CategoriaProdAdmin)
admin.site.register(Producto, ProductoAdmin)