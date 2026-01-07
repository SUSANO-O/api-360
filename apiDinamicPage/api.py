from rest_framework import viewsets, permissions, status
from .models import Template, User, DataForm, Profile, QrdataForm, UserImage, ApiUrl, VCard
from .serializers import TemplateSerializer, UserSerializer, DataFormSerializer, RegisterSerializer, ProfileSerializer, MyTokenObtainPairSerializer,QrdataFormSerializer, ProfileImageSerializer, UserImageSerializer, UserImageCreateSerializer, ApiUrlSerializer, VCardSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TemplateSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

class DataFormViewSet(viewsets.ModelViewSet):
    queryset = DataForm.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DataFormSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    
    @action(detail=False, methods=['post'], url_path='upload-image-base64')
    def upload_image_base64(self, request):
        """
        Endpoint para subir imagen en base64 para un usuario específico
        """
        try:
            user_id = request.data.get('user_id')
            image_base64 = request.data.get('image_base64')
            
            if not user_id:
                return Response(
                    {'error': 'user_id es requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not image_base64:
                return Response(
                    {'error': 'image_base64 es requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar el usuario
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener o crear el perfil
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Actualizar la imagen base64
            serializer = ProfileImageSerializer(profile, data={'image_base64': image_base64}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Imagen guardada exitosamente',
                    'profile_id': profile.id,
                    'user_id': user.id,
                    'username': user.username
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='get-image-base64/(?P<user_id>[^/.]+)')
    def get_image_base64(self, request, user_id=None):
        """
        Endpoint para obtener imagen base64 de un usuario específico
        """
        try:
            # Buscar el usuario
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener el perfil
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Perfil no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'user_id': user.id,
                'username': user.username,
                'image_base64': profile.image_base64,
                'has_image': bool(profile.image_base64)
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
        })


class TokenObtainPairView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

class QrCodeViewSet(viewsets.ModelViewSet):
    queryset = QrdataForm.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QrdataFormSerializer

class UserImageViewSet(viewsets.ModelViewSet):
    queryset = UserImage.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserImageSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserImageCreateSerializer
        return UserImageSerializer
    
    def get_queryset(self):
        queryset = UserImage.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        user_email = self.request.query_params.get('user_email', None)
        category = self.request.query_params.get('category', None)
        is_public = self.request.query_params.get('is_public', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if user_email:
            queryset = queryset.filter(user__email=user_email)
        if category:
            queryset = queryset.filter(category=category)
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
            
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['post'], url_path='upload-multiple')
    def upload_multiple_images(self, request):
        """
        Endpoint para subir múltiples imágenes al mismo usuario
        """
        try:
            user_id = request.data.get('user_id')
            images = request.data.get('images', [])
            
            if not user_id:
                return Response(
                    {'error': 'user_id es requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not images or not isinstance(images, list):
                return Response(
                    {'error': 'images debe ser un array de imágenes'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar el usuario
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            created_images = []
            errors = []
            
            for i, image_data in enumerate(images):
                try:
                    # Agregar user_id a cada imagen
                    image_data['user'] = user_id
                    
                    serializer = UserImageCreateSerializer(data=image_data)
                    if serializer.is_valid():
                        image_instance = serializer.save()
                        created_images.append({
                            'id': image_instance.id,
                            'title': image_instance.title,
                            'category': image_instance.category,
                            'created_at': image_instance.created_at
                        })
                    else:
                        errors.append({
                            'index': i,
                            'errors': serializer.errors
                        })
                except Exception as e:
                    errors.append({
                        'index': i,
                        'error': str(e)
                    })
            
            return Response({
                'message': f'{len(created_images)} imágenes guardadas exitosamente',
                'user_id': user_id,
                'username': user.username,
                'created_images': created_images,
                'errors': errors if errors else None,
                'total_uploaded': len(created_images),
                'total_failed': len(errors)
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_user_images(self, request, user_id=None):
        """
        Endpoint para obtener todas las imágenes de un usuario específico
        """
        try:
            # Buscar el usuario
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Filtrar imágenes del usuario
            images = UserImage.objects.filter(user=user).order_by('-created_at')
            
            # Aplicar filtros adicionales si existen
            category = request.query_params.get('category', None)
            is_public = request.query_params.get('is_public', None)
            
            if category:
                images = images.filter(category=category)
            if is_public is not None:
                images = images.filter(is_public=is_public.lower() == 'true')
            
            serializer = UserImageSerializer(images, many=True)
            
            return Response({
                'user_id': user.id,
                'username': user.username,
                'total_images': images.count(),
                'images': serializer.data
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'], url_path='delete-multiple')
    def delete_multiple_images(self, request):
        """
        Endpoint para eliminar múltiples imágenes por ID
        """
        try:
            image_ids = request.data.get('image_ids', [])
            
            if not image_ids or not isinstance(image_ids, list):
                return Response(
                    {'error': 'image_ids debe ser un array de IDs'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar las imágenes
            images = UserImage.objects.filter(id__in=image_ids)
            deleted_count = images.count()
            
            if deleted_count == 0:
                return Response(
                    {'error': 'No se encontraron imágenes con los IDs proporcionados'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Eliminar las imágenes
            images.delete()
            
            return Response({
                'message': f'{deleted_count} imágenes eliminadas exitosamente',
                'deleted_ids': image_ids,
                'total_deleted': deleted_count
            }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ApiUrlViewSet(viewsets.ModelViewSet):
    queryset = ApiUrl.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ApiUrlSerializer
    
    def list(self, request):
        """
        Devuelve un JSON con todas las URLs de la API en formato diccionario
        """
        # Obtener todas las URLs de la base de datos
        api_urls = ApiUrl.objects.all()
        
        # Construir el diccionario de URLs
        urls_dict = {}
        for api_url in api_urls:
            urls_dict[api_url.name] = api_url.url
        
        # Si no hay URLs en la base de datos, devolver URLs por defecto
        if not urls_dict:
            # Construir la URL base
            request_scheme = request.scheme  # http o https
            request_host = request.get_host()  # 127.0.0.1:8000 o dominio
            
            base_url = f"{request_scheme}://{request_host}/api/v1/"
            
            urls_dict = {
                "template": f"{base_url}template/",
                "user": f"{base_url}user/",
                "dataform": f"{base_url}dataform/",
                "profile": f"{base_url}profile/",
                "register": f"{base_url}register/",
                "token": f"{base_url}token/",
                "qr": f"{base_url}qr/",
                "userimage": f"{base_url}userimage/",
            }
        
        return Response(urls_dict, status=status.HTTP_200_OK)

class VCardViewSet(viewsets.ModelViewSet):
    queryset = VCard.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = VCardSerializer