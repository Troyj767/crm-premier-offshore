# backend/crm/admin.py
from django.contrib import admin
from .models import Rol, Usuario, Contacto, Interaccion, Oportunidad, Tarea, LogAuditoria


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre_rol', 'descripcion']
    search_fields = ['nombre_rol']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display   = ['id', 'nombre', 'correo', 'id_rol', 'activo', 'fecha_creacion']
    list_filter    = ['id_rol', 'activo']
    search_fields  = ['nombre', 'correo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    exclude        = ['contrasena_hash']


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nombre', 'empresa', 'pais', 'estado', 'id_agente_asignado']
    list_filter   = ['estado', 'pais', 'idioma_preferido']
    search_fields = ['nombre', 'empresa', 'correo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Interaccion)
class InteraccionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'id_contacto', 'id_usuario', 'tipo_interaccion', 'fecha_hora']
    list_filter   = ['tipo_interaccion']
    search_fields = ['id_contacto__nombre', 'resultado']
    readonly_fields = ['fecha_hora']


@admin.register(Oportunidad)
class OportunidadAdmin(admin.ModelAdmin):
    list_display  = ['id', 'titulo', 'id_contacto', 'etapa',
                     'monto_estimado', 'probabilidad_pct', 'fecha_cierre_est']
    list_filter   = ['etapa']
    search_fields = ['titulo', 'id_contacto__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'titulo', 'estado', 'prioridad',
                     'id_usuario_asignado', 'fecha_limite']
    list_filter   = ['estado', 'prioridad']
    search_fields = ['titulo', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'id_usuario', 'accion', 'tabla_afectada',
                     'id_registro', 'ip_origen', 'fecha_hora']
    list_filter   = ['accion', 'tabla_afectada']
    search_fields = ['id_usuario__nombre', 'tabla_afectada']
    readonly_fields = ['fecha_hora']
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False