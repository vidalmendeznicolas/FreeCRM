from django.contrib import admin
from .models import Categoria, Post
# Register your models here.
class CategoriaAdmin(admin.ModelAdmin):
    readonly_fields=('created', 'updated')
    list_display=('nombre', 'created', 'updated')
    ordering=('created',)
    search_fields=('nombre',)
    list_filter=('nombre',)

class PostAdmin(admin.ModelAdmin):
    readonly_fields=('created', 'updated')
    list_display=('titulo', 'autor','created')
    ordering=('created',)
    search_fields=('titulo', 'autor__username', 'categorias__nombre')
    list_filter=('categorias__nombre',)

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Post, PostAdmin)