from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import Carrera, Materia, Alumno, Inscripcion, Publicacion, Card
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]

class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id', 'nombre', 'clave', 'descripcion', 'materias']


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = '__all__'


class AlumnoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)
    apellido_paterno = serializers.CharField(required=True)
    apellido_materno = serializers.CharField(required=True)
    numero_control = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=Alumno.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Alumno.objects.all())]
    )
    carrera = serializers.PrimaryKeyRelatedField(
        queryset=Carrera.objects.all(),
        required=True
    )

    class Meta:
        model = Alumno
        fields = '__all__'

    # Validaciones personalizadas
    def validate_nombre(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return value

    def validate_apellido_paterno(self, value):
        if not value.strip():
            raise serializers.ValidationError("El apellido paterno es obligatorio.")
        return value

    def validate_apellido_materno(self, value):
        if not value.strip():
            raise serializers.ValidationError("El apellido materno es obligatorio.")
        return value

    def validate_numero_control(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("El número de control debe ser numérico.")
        return value


class InscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscripcion
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]  # 👈 valida que no exista
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]   # 👈 aplica validadores de settings.py
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user


class MeUserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "groups",
            "date_joined",
        ]
        read_only_fields = fields


class MeUserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="Este correo electrónico ya está registrado por otro usuario."
        )]
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {
            "username": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance