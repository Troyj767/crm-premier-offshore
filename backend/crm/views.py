# backend/crm/views.py
import json
from django.utils import timezone
from django.db.models import Count, Sum, Q
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Rol, Usuario, Contacto, Interaccion, Oportunidad, Tarea, LogAuditoria
from .serializers import (
    RolSerializer, UsuarioSerializer, UsuarioCreateSerializer,
    ContactoSerializer, InteraccionSerializer,
    OportunidadSerializer, TareaSerializer, LogAuditoriaSerializer,
)


# ─── Utilidad de auditoría ────────────────────────────────────────────────────
def registrar_log(request, accion, tabla, id_registro=None, anterior=None, nuevo=None):
    """Crea un registro en Log_Auditoria automáticamente."""
    try:
        usuario_id = request.META.get('HTTP_X_USUARIO_ID')  # Header personalizado
        if usuario_id:
            LogAuditoria.objects.create(
                id_usuario_id  = usuario_id,
                accion         = accion,
                tabla_afectada = tabla,
                id_registro    = id_registro,
                valor_anterior = json.dumps(anterior, ensure_ascii=False) if anterior else None,
                valor_nuevo    = json.dumps(nuevo,    ensure_ascii=False) if nuevo    else None,
                ip_origen      = request.META.get('REMOTE_ADDR'),
            )
    except Exception:
        pass  # El log nunca debe romper la operación principal


# ─── Roles ────────────────────────────────────────────────────────────────────
class RolViewSet(viewsets.ModelViewSet):
    queryset         = Rol.objects.all()
    serializer_class = RolSerializer


# ─── Usuarios ─────────────────────────────────────────────────────────────────
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related('id_rol').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ['nombre', 'correo']
    ordering_fields = ['nombre', 'fecha_creacion']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        registrar_log(self.request, 'Creacion', 'Usuarios', obj.id,
                      nuevo={'correo': obj.correo, 'rol': obj.id_rol_id})

    def perform_update(self, serializer):
        anterior = UsuarioSerializer(self.get_object()).data
        obj = serializer.save()
        registrar_log(self.request, 'Edicion', 'Usuarios', obj.id,
                      anterior=anterior, nuevo=UsuarioSerializer(obj).data)

    def perform_destroy(self, instance):
        anterior = UsuarioSerializer(instance).data
        registrar_log(self.request, 'Eliminacion', 'Usuarios', instance.id, anterior=anterior)
        instance.delete()


# ─── Contactos ────────────────────────────────────────────────────────────────
class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.select_related('id_agente_asignado').all()
    serializer_class = ContactoSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['nombre', 'empresa', 'correo', 'pais']
    ordering_fields  = ['nombre', 'empresa', 'fecha_creacion', 'estado']

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get('estado')
        agente = self.request.query_params.get('agente')
        if estado:
            qs = qs.filter(estado=estado)
        if agente:
            qs = qs.filter(id_agente_asignado=agente)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        registrar_log(self.request, 'Creacion', 'Contactos', obj.id,
                      nuevo={'nombre': obj.nombre, 'empresa': obj.empresa})

    def perform_update(self, serializer):
        anterior = ContactoSerializer(self.get_object()).data
        obj = serializer.save()
        registrar_log(self.request, 'Edicion', 'Contactos', obj.id,
                      anterior=anterior, nuevo=ContactoSerializer(obj).data)

    def perform_destroy(self, instance):
        anterior = ContactoSerializer(instance).data
        registrar_log(self.request, 'Eliminacion', 'Contactos', instance.id, anterior=anterior)
        instance.delete()

    @action(detail=True, methods=['get'])
    def historial(self, request, pk=None):
        """GET /api/contactos/{id}/historial/ — todas las interacciones del contacto."""
        contacto = self.get_object()
        interacciones = contacto.interacciones.select_related('id_usuario').order_by('-fecha_hora')
        serializer = InteraccionSerializer(interacciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pipeline(self, request, pk=None):
        """GET /api/contactos/{id}/pipeline/ — oportunidades del contacto."""
        contacto = self.get_object()
        oportunidades = contacto.oportunidades.select_related('id_usuario').all()
        serializer = OportunidadSerializer(oportunidades, many=True)
        return Response(serializer.data)


# ─── Interacciones ────────────────────────────────────────────────────────────
class InteraccionViewSet(viewsets.ModelViewSet):
    queryset = Interaccion.objects.select_related('id_contacto', 'id_usuario').all()
    serializer_class = InteraccionSerializer
    filter_backends  = [filters.OrderingFilter]
    ordering_fields  = ['fecha_hora', 'tipo_interaccion']

    def get_queryset(self):
        qs = super().get_queryset()
        contacto = self.request.query_params.get('contacto')
        tipo     = self.request.query_params.get('tipo')
        if contacto:
            qs = qs.filter(id_contacto=contacto)
        if tipo:
            qs = qs.filter(tipo_interaccion=tipo)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        registrar_log(self.request, 'Creacion', 'Interacciones', obj.id,
                      nuevo={'tipo': obj.tipo_interaccion, 'contacto': obj.id_contacto_id})

    def perform_update(self, serializer):
        anterior = InteraccionSerializer(self.get_object()).data
        obj = serializer.save()
        registrar_log(self.request, 'Edicion', 'Interacciones', obj.id,
                      anterior=anterior, nuevo=InteraccionSerializer(obj).data)

    def perform_destroy(self, instance):
        registrar_log(self.request, 'Eliminacion', 'Interacciones', instance.id,
                      anterior=InteraccionSerializer(instance).data)
        instance.delete()


# ─── Oportunidades ────────────────────────────────────────────────────────────
class OportunidadViewSet(viewsets.ModelViewSet):
    queryset = Oportunidad.objects.select_related('id_contacto', 'id_usuario').all()
    serializer_class = OportunidadSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['titulo', 'id_contacto__nombre']
    ordering_fields  = ['etapa', 'monto_estimado', 'fecha_cierre_est']

    def get_queryset(self):
        qs = super().get_queryset()
        etapa   = self.request.query_params.get('etapa')
        agente  = self.request.query_params.get('agente')
        if etapa:
            qs = qs.filter(etapa=etapa)
        if agente:
            qs = qs.filter(id_usuario=agente)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        registrar_log(self.request, 'Creacion', 'Oportunidades', obj.id,
                      nuevo={'titulo': obj.titulo, 'etapa': obj.etapa})

    def perform_update(self, serializer):
        anterior = OportunidadSerializer(self.get_object()).data
        obj = serializer.save()
        registrar_log(self.request, 'Edicion', 'Oportunidades', obj.id,
                      anterior=anterior, nuevo=OportunidadSerializer(obj).data)

    def perform_destroy(self, instance):
        registrar_log(self.request, 'Eliminacion', 'Oportunidades', instance.id,
                      anterior=OportunidadSerializer(instance).data)
        instance.delete()

    @action(detail=False, methods=['get'])
    def por_etapa(self, request):
        """GET /api/oportunidades/por_etapa/ — resumen para el tablero Kanban."""
        data = (Oportunidad.objects
                .values('etapa')
                .annotate(total=Count('id'), valor=Sum('monto_estimado'))
                .order_by('etapa'))
        return Response(list(data))


# ─── Tareas ───────────────────────────────────────────────────────────────────
class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.select_related('id_usuario_asignado', 'id_contacto').all()
    serializer_class = TareaSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['titulo', 'descripcion']
    ordering_fields  = ['fecha_limite', 'prioridad', 'estado']

    def get_queryset(self):
        qs = super().get_queryset()
        estado   = self.request.query_params.get('estado')
        agente   = self.request.query_params.get('agente')
        prioridad = self.request.query_params.get('prioridad')
        if estado:
            qs = qs.filter(estado=estado)
        if agente:
            qs = qs.filter(id_usuario_asignado=agente)
        if prioridad:
            qs = qs.filter(prioridad=prioridad)
        return qs

    def perform_create(self, serializer):
        obj = serializer.save()
        registrar_log(self.request, 'Creacion', 'Tareas', obj.id,
                      nuevo={'titulo': obj.titulo, 'estado': obj.estado})

    def perform_update(self, serializer):
        anterior = TareaSerializer(self.get_object()).data
        obj = serializer.save()
        registrar_log(self.request, 'Edicion', 'Tareas', obj.id,
                      anterior=anterior, nuevo=TareaSerializer(obj).data)

    def perform_destroy(self, instance):
        registrar_log(self.request, 'Eliminacion', 'Tareas', instance.id,
                      anterior=TareaSerializer(instance).data)
        instance.delete()

    @action(detail=False, methods=['get'])
    def urgentes(self, request):
        """GET /api/tareas/urgentes/ — tareas vencidas o que vencen en 48 horas."""
        limite = timezone.now() + timezone.timedelta(hours=48)
        qs = self.get_queryset().filter(
            ~Q(estado='Completada'),
            fecha_limite__lte=limite
        ).order_by('fecha_limite')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# ─── Dashboard / KPIs ─────────────────────────────────────────────────────────
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def dashboard_kpis(request):
    """GET /api/dashboard/ — KPIs principales para el panel de control (RF-11)."""
    hoy = timezone.now()

    contactos_activos  = Contacto.objects.filter(estado='Activo').count()
    contactos_nuevos   = Contacto.objects.filter(fecha_creacion__month=hoy.month).count()
    tareas_pendientes  = Tarea.objects.filter(estado='Pendiente').count()
    tareas_vencidas    = Tarea.objects.filter(estado__in=['Pendiente','En Progreso'], fecha_limite__lt=hoy).count()

    pipeline = list(
        Oportunidad.objects
        .values('etapa')
        .annotate(total=Count('id'), valor=Sum('monto_estimado'))
        .order_by('etapa')
    )

    interacciones_mes = Interaccion.objects.filter(fecha_hora__month=hoy.month).count()

    oportunidades_ganadas = Oportunidad.objects.filter(etapa='Cerrado Ganado').count()
    oportunidades_total   = Oportunidad.objects.exclude(etapa__in=['Prospecto']).count()
    tasa_conversion = round((oportunidades_ganadas / oportunidades_total * 100), 1) if oportunidades_total else 0

    return Response({
        'contactos_activos':   contactos_activos,
        'contactos_nuevos_mes': contactos_nuevos,
        'tareas_pendientes':   tareas_pendientes,
        'tareas_vencidas':     tareas_vencidas,
        'interacciones_mes':   interacciones_mes,
        'tasa_conversion_pct': tasa_conversion,
        'pipeline_por_etapa':  pipeline,
    })


# ─── Auditoría ────────────────────────────────────────────────────────────────
class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo lectura — nadie puede modificar los logs."""
    queryset = LogAuditoria.objects.select_related('id_usuario').all()
    serializer_class = LogAuditoriaSerializer
    filter_backends  = [filters.OrderingFilter]
    ordering_fields  = ['fecha_hora', 'accion', 'tabla_afectada']

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = self.request.query_params.get('usuario')
        accion  = self.request.query_params.get('accion')
        tabla   = self.request.query_params.get('tabla')
        if usuario:
            qs = qs.filter(id_usuario=usuario)
        if accion:
            qs = qs.filter(accion=accion)
        if tabla:
            qs = qs.filter(tabla_afectada=tabla)
        return qs
