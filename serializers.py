# backend/crm/serializers.py
from rest_framework import serializers
from .models import Rol, Usuario, Contacto, Interaccion, Oportunidad, Tarea, LogAuditoria


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Rol
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='id_rol.nombre_rol', read_only=True)

    class Meta:
        model  = Usuario
        fields = ['id', 'nombre', 'correo', 'id_rol', 'rol_nombre', 'activo',
                  'fecha_creacion', 'fecha_actualizacion']
        # contrasena_hash se excluye siempre de la respuesta


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer especial para crear/actualizar usuario con contraseña."""
    class Meta:
        model  = Usuario
        fields = ['nombre', 'correo', 'contrasena_hash', 'id_rol', 'activo']

    def create(self, validated_data):
        import bcrypt
        raw = validated_data.pop('contrasena_hash')
        hashed = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
        return Usuario.objects.create(contrasena_hash=hashed, **validated_data)


class ContactoSerializer(serializers.ModelSerializer):
    agente_nombre = serializers.CharField(source='id_agente_asignado.nombre', read_only=True)

    class Meta:
        model  = Contacto
        fields = '__all__'
        extra_fields = ['agente_nombre']

    def get_fields(self):
        fields = super().get_fields()
        fields['agente_nombre'] = serializers.CharField(
            source='id_agente_asignado.nombre', read_only=True
        )
        return fields


class InteraccionSerializer(serializers.ModelSerializer):
    contacto_nombre = serializers.CharField(source='id_contacto.nombre', read_only=True)
    agente_nombre   = serializers.CharField(source='id_usuario.nombre',  read_only=True)

    class Meta:
        model  = Interaccion
        fields = '__all__'


class OportunidadSerializer(serializers.ModelSerializer):
    contacto_nombre = serializers.CharField(source='id_contacto.nombre', read_only=True)
    agente_nombre   = serializers.CharField(source='id_usuario.nombre',  read_only=True)

    class Meta:
        model  = Oportunidad
        fields = '__all__'

    def validate_probabilidad_pct(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("La probabilidad debe estar entre 0 y 100.")
        return value


class TareaSerializer(serializers.ModelSerializer):
    agente_nombre   = serializers.CharField(source='id_usuario_asignado.nombre', read_only=True)
    contacto_nombre = serializers.CharField(source='id_contacto.nombre',         read_only=True)
    vencida         = serializers.SerializerMethodField()

    class Meta:
        model  = Tarea
        fields = '__all__'

    def get_vencida(self, obj):
        from django.utils import timezone
        return obj.estado != 'Completada' and obj.fecha_limite < timezone.now()


class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='id_usuario.nombre', read_only=True)

    class Meta:
        model  = LogAuditoria
        fields = '__all__'
