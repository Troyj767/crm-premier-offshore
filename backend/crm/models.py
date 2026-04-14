# backend/crm/models.py
from django.db import models
from django.utils import timezone


class Rol(models.Model):
    nombre_rol     = models.CharField(max_length=50, unique=True)
    descripcion    = models.CharField(max_length=255, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre_rol


class Usuario(models.Model):
    nombre              = models.CharField(max_length=100)
    correo              = models.EmailField(unique=True)
    contrasena_hash     = models.CharField(max_length=255)
    id_rol              = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column='id_rol')
    activo              = models.BooleanField(default=True)
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Requerido por Django REST Framework para verificar permisos
    is_authenticated = True
    is_active        = True
    is_staff         = False
    is_superuser     = False

    class Meta:
        db_table = 'Usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} ({self.id_rol.nombre_rol})"


class Contacto(models.Model):
    ESTADO_CHOICES = [('Activo', 'Activo'), ('Inactivo', 'Inactivo')]

    nombre             = models.CharField(max_length=100)
    empresa            = models.CharField(max_length=100, blank=True)
    telefono           = models.CharField(max_length=20, blank=True)
    correo             = models.EmailField(blank=True)
    pais               = models.CharField(max_length=50, blank=True)
    idioma_preferido   = models.CharField(max_length=20, blank=True)
    estado             = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Activo')
    id_agente_asignado = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        db_column='id_agente_asignado', related_name='contactos'
    )
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Contactos'
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['empresa']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.nombre} — {self.empresa}"


class Interaccion(models.Model):
    TIPO_CHOICES = [
        ('Llamada', 'Llamada'), ('Correo', 'Correo'),
        ('Chat', 'Chat'), ('Reunion', 'Reunión'), ('Otro', 'Otro'),
    ]

    id_contacto      = models.ForeignKey(Contacto, on_delete=models.CASCADE, db_column='id_contacto', related_name='interacciones')
    id_usuario       = models.ForeignKey(Usuario,  on_delete=models.PROTECT,  db_column='id_usuario')
    tipo_interaccion = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_hora       = models.DateTimeField(default=timezone.now)
    duracion_minutos = models.PositiveIntegerField(default=0)
    resultado        = models.TextField(blank=True)
    notas_internas   = models.TextField(blank=True)

    class Meta:
        db_table = 'Interacciones'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.tipo_interaccion} — {self.id_contacto.nombre} ({self.fecha_hora:%Y-%m-%d})"


class Oportunidad(models.Model):
    ETAPA_CHOICES = [
        ('Prospecto',       'Prospecto'),
        ('Contactado',      'Contactado'),
        ('Propuesta',       'Propuesta'),
        ('Negociacion',     'Negociación'),
        ('Cerrado Ganado',  'Cerrado Ganado'),
        ('Cerrado Perdido', 'Cerrado Perdido'),
    ]

    titulo              = models.CharField(max_length=150)
    id_contacto         = models.ForeignKey(Contacto, on_delete=models.CASCADE, db_column='id_contacto', related_name='oportunidades')
    id_usuario          = models.ForeignKey(Usuario,  on_delete=models.PROTECT,  db_column='id_usuario')
    etapa               = models.CharField(max_length=50, choices=ETAPA_CHOICES, default='Prospecto')
    monto_estimado      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    probabilidad_pct    = models.PositiveSmallIntegerField(default=0)
    fecha_cierre_est    = models.DateField(null=True, blank=True)
    descripcion         = models.TextField(blank=True)
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Oportunidades'
        indexes = [models.Index(fields=['etapa'])]

    def __str__(self):
        return f"{self.titulo} [{self.etapa}]"


class Tarea(models.Model):
    ESTADO_CHOICES    = [('Pendiente','Pendiente'),('En Progreso','En Progreso'),('Completada','Completada'),('Vencida','Vencida')]
    PRIORIDAD_CHOICES = [('Baja','Baja'),('Normal','Normal'),('Alta','Alta'),('Urgente','Urgente')]

    titulo               = models.CharField(max_length=150)
    descripcion          = models.TextField()
    fecha_limite         = models.DateTimeField()
    estado               = models.CharField(max_length=20, choices=ESTADO_CHOICES,    default='Pendiente')
    prioridad            = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='Normal')
    id_usuario_asignado  = models.ForeignKey(Usuario,  on_delete=models.PROTECT,  db_column='id_usuario_asignado', related_name='tareas')
    id_contacto          = models.ForeignKey(Contacto, on_delete=models.SET_NULL, db_column='id_contacto', null=True, blank=True, related_name='tareas')
    notificacion_enviada = models.BooleanField(default=False)
    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Tareas'
        ordering = ['fecha_limite']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_limite']),
        ]

    def __str__(self):
        return f"{self.titulo} [{self.estado}]"


class LogAuditoria(models.Model):
    ACCION_CHOICES = [
        ('Creacion','Creación'),('Edicion','Edición'),
        ('Eliminacion','Eliminación'),('Login','Login'),('Logout','Logout'),
    ]

    id_usuario     = models.ForeignKey(Usuario, on_delete=models.PROTECT, db_column='id_usuario')
    accion         = models.CharField(max_length=50, choices=ACCION_CHOICES)
    tabla_afectada = models.CharField(max_length=50)
    id_registro    = models.IntegerField(null=True, blank=True)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_nuevo    = models.TextField(null=True, blank=True)
    ip_origen      = models.GenericIPAddressField(null=True, blank=True)
    fecha_hora     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Log_Auditoria'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.accion} en {self.tabla_afectada} por {self.id_usuario.nombre}"