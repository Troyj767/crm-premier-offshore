# backend/crm/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework import exceptions
from .models import Usuario


class UsuarioJWTAuthentication(JWTAuthentication):
    """
    Autenticacion JWT custom que usa nuestro modelo Usuario
    en vez del auth_user de Django.
    """

    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token no contiene user_id')

        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                id=user_id, activo=True
            )
        except Usuario.DoesNotExist:
            raise exceptions.AuthenticationFailed('Usuario no encontrado o inactivo')

        return usuario
