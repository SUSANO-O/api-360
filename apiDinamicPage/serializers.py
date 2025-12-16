from rest_framework import serializers
from .models import Template, User, DataForm, Profile, QrdataForm, UserImage, ApiUrl

from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'
        read_only_fields = ('created_at',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('created_at',)


class DataFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataForm
        fields = '__all__'
        read_only_fields = ('created_at',)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        print(user, 'user')
        token = super().get_token(user)

        # Add custom claims
        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['email'] = user.email
        token['bio'] = user.profile.bio
        token['verified'] = user.profile.verified


        return token
# Compare this snippet from apiDinamicPage/views.py:
# @api_view(['POST', 'GET','PUT'])
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password2')     

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    
    def create(self, request, *args, **kwargs):
        user = User.objects.create(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        user.set_password(self.validated_data['password'])
        user.save()

        return user
    
    def update(self, request, *args, **kwargs):
        user = self.instance
        user.email = self.validated_data['email']
        user.username = self.validated_data['username']
        user.set_password(self.validated_data['password'])
        user.save()

        return user

class QrdataFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = QrdataForm
        fields = '__all__'
        read_only_fields = ('created_at',)

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image_base64']
    
    def validate_image_base64(self, value):
        if not value:
            return value
        
        # Validar que sea base64 válido
        import base64
        try:
            # Remover el prefijo data:image si existe
            if ',' in value:
                value = value.split(',')[1]
            
            # Decodificar para verificar que es válido
            base64.b64decode(value)
            return value
        except Exception:
            raise serializers.ValidationError("Formato base64 inválido")

class UserImageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserImage
        fields = [
            'id', 'user', 'username', 'user_email', 'title', 'description', 
            'image', 'image_base64', 'image_type', 'file_size', 'category', 
            'is_public', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'file_size')
    
    def validate_image_base64(self, value):
        if not value:
            raise serializers.ValidationError("image_base64 es requerido")
        
        # Validar que sea base64 válido
        import base64
        try:
            # Remover el prefijo data:image si existe
            if ',' in value:
                header, data = value.split(',', 1)
                # Extraer el tipo de imagen del header
                if 'image/' in header:
                    image_type = header.split('/')[-1].split(';')[0]
                    self.context['image_type'] = image_type
                value = data
            
            # Decodificar para verificar que es válido
            decoded_data = base64.b64decode(value)
            
            # Calcular el tamaño del archivo
            self.context['file_size'] = len(decoded_data)
            
            return value
        except Exception:
            raise serializers.ValidationError("Formato base64 inválido")
    
    def create(self, validated_data):
        # Agregar el tipo de imagen y tamaño del archivo si están en el contexto
        if 'image_type' in self.context:
            validated_data['image_type'] = self.context['image_type']
        if 'file_size' in self.context:
            validated_data['file_size'] = self.context['file_size']
        
        return super().create(validated_data)

class UserImageCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear imágenes"""
    class Meta:
        model = UserImage
        fields = ['user', 'title', 'description', 'image', 'category', 'is_public', 'tags']
        extra_kwargs = {
            'user': {'required': False},
            'title': {'required': False},
            'description': {'required': False},
            'image': {'required': True},
            'category': {'required': False},
            'is_public': {'required': False},
            'tags': {'required': False},
        }
    
    def validate(self, attrs):
        # Validar que se proporcione una imagen
        if not attrs.get('image'):
            raise serializers.ValidationError("Debe proporcionar una imagen")
        return attrs
    
    def create(self, validated_data):
        # Si no se proporciona user, usar un usuario por defecto (opcional)
        if 'user' not in validated_data or validated_data['user'] is None:
            # Puedes cambiar esto por lógica específica de tu aplicación
            from .models import User
            try:
                default_user = User.objects.first()
                if default_user:
                    validated_data['user'] = default_user
                else:
                    raise serializers.ValidationError("No hay usuarios disponibles y no se especificó un usuario")
            except:
                raise serializers.ValidationError("Usuario requerido")
        
        # Convertir la imagen a base64
        image_file = validated_data.get('image')
        if image_file:
            import base64
            import io
            
            # Leer el archivo de imagen
            image_file.seek(0)  # Asegurar que estamos al inicio del archivo
            image_data = image_file.read()
            
            # Convertir a base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Agregar el tipo de imagen basado en la extensión
            file_extension = image_file.name.split('.')[-1].lower()
            image_type = file_extension if file_extension in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'] else 'png'
            
            # Calcular el tamaño del archivo
            file_size = len(image_data)
            
            # Agregar los datos calculados
            validated_data['image_base64'] = image_base64
            validated_data['image_type'] = image_type
            validated_data['file_size'] = file_size
        
        return super().create(validated_data)

class ApiUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiUrl
        fields = ['id', 'name', 'url', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')