# backend/crm/auth.py
import bcrypt
from django.utils import timezone
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models      import Usuario, LogAuditoria
from .serializers import UsuarioSerializer


def _ip(request):
    """Obtiene la IP real del cliente, considerando proxies."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')


class LoginView(APIView):
    """
    POST /api/auth/token/
    Body: { "correo": "...", "contrasena": "..." }
    Devuelve: { "access": "...", "refresh": "...", "usuario": {...} }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        correo    = request.data.get('correo', '').strip().lower()
        contrasena = request.data.get('contrasena', '')

        if not correo or not contrasena:
            return Response(
                {'error': 'Correo y contraseña son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar usuario por correo
        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                correo__iexact=correo, activo=True
            )
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Credenciales incorrectas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verificar contraseña con bcrypt
        try:
            hash_valido = bcrypt.checkpw(
                contrasena.encode('utf-8'),
                usuario.contrasena_hash.encode('utf-8')
            )
        except Exception:
            hash_valido = False

        if not hash_valido:
            return Response(
                {'error': 'Credenciales incorrectas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Generar tokens JWT
        refresh = RefreshToken.for_user(usuario)

        # Registrar login en auditoría
        LogAuditoria.objects.create(
            id_usuario     = usuario,
            accion         = 'Login',
            tabla_afectada = 'Usuarios',
            id_registro    = usuario.id,
            valor_nuevo    = f'{{"correo": "{usuario.correo}"}}',
            ip_origen      = _ip(request),
        )

        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': {
                'id':     usuario.id,
                'nombre': usuario.nombre,
                'correo': usuario.correo,
                'rol':    usuario.id_rol.nombre_rol,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Body: { "refresh": "..." }
    Invalida el refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()

            # Registrar logout en auditoría
            usuario_id = request.META.get('HTTP_X_USUARIO_ID')
            if usuario_id:
                LogAuditoria.objects.create(
                    id_usuario_id  = usuario_id,
                    accion         = 'Logout',
                    tabla_afectada = 'Usuarios',
                    id_registro    = usuario_id,
                    ip_origen      = _ip(request),
                )
        except Exception:
            pass

        return Response({'mensaje': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)
