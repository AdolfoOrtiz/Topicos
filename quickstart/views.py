from django.contrib.auth.models import Group, User
from django.contrib.auth import logout as django_logout
from rest_framework import permissions, viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from quickstart.authentication import BearerTokenAuthentication

from quickstart.serializers import (
    GroupSerializer, UserSerializer,
    CarreraSerializer, MateriaSerializer,
    AlumnoSerializer, InscripcionSerializer, CardSerializer, RegisterSerializer,
    MeUserSerializer, MeUserUpdateSerializer
)
from quickstart.models import Carrera, Materia, Alumno, Inscripcion, Card



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer
    permission_classes = [permissions.IsAuthenticated]


class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [permissions.IsAuthenticated]


class AlumnoViewSet(viewsets.ModelViewSet):
    queryset = Alumno.objects.all().order_by('id')
    serializer_class = AlumnoSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 🔹 Filtros, búsqueda y ordenamiento
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['carrera']   # Filtrar por carrera
    search_fields = ['nombre', 'apellido_paterno', 'numero_control', 'email']  # Buscar por estos campos
    ordering_fields = ['nombre', 'numero_control']  # Ordenar por estos campos


class InscripcionViewSet(viewsets.ModelViewSet):
    queryset = Inscripcion.objects.all()
    serializer_class = InscripcionSerializer
    permission_classes = [permissions.IsAuthenticated]


class CardViewSet(viewsets.ModelViewSet):
    """
    API endpoint para listar, crear, ver, actualizar y eliminar cartas (Card).
    """
    queryset = Card.objects.all().order_by('id')
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['id', 'nombre']



class CustomAuthToken(ObtainAuthToken):
    """
    Endpoint para obtener un token junto con información del usuario.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class RegisterAPIView(APIView):
    """
    API para registrar nuevos usuarios y devolver su token.
    """
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeAPIView(APIView):
    """
    Endpoint para obtener y editar la información del usuario autenticado mediante su Token.
    Soporta GET, PATCH, POST y PUT.
    Soporta autenticación con encabezado 'Token <token>' o 'Bearer <token>'.
    """
    authentication_classes = [TokenAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeUserSerializer(request.user)
        data = serializer.data
        if request.auth:
            data["auth_token"] = str(request.auth)
        return Response(data)

    def patch(self, request):
        serializer = MeUserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = MeUserSerializer(request.user).data
            if request.auth:
                data["auth_token"] = str(request.auth)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        return self.patch(request)

    def put(self, request):
        return self.patch(request)


class ResetTokenAPIView(APIView):
    """
    Endpoint para regenerar/cambiar el token del usuario autenticado.
    Elimina el token actual y genera uno nuevo.
    Requiere enviar el token actual en los encabezados (Token o Bearer).
    """
    authentication_classes = [TokenAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        # Eliminar cualquier token existente para este usuario
        Token.objects.filter(user=user).delete()
        # Generar nuevo token
        new_token = Token.objects.create(user=user)
        return Response({
            "detail": "Token renovado exitosamente.",
            "token": new_token.key,
            "user_id": user.pk,
            "username": user.username
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    """
    Endpoint para cerrar sesión y desautenticar al usuario.
    Elimina el token de la base de datos para invalidarlo inmediatamente.
    """
    authentication_classes = [TokenAuthentication, BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Eliminar el token para que ya no sea válido
        Token.objects.filter(user=request.user).delete()
        # Cerrar sesión en caso de que exista sesión por cookie
        django_logout(request)
        return Response({
            "detail": "Sesión cerrada exitosamente. Token eliminado."
        }, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)