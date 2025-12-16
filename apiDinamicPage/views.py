from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, status, generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
import rest_framework.permissions as permissions
from .models import Template, DataForm, User, QrdataForm
from .serializers import TemplateSerializer, DataFormSerializer, MyTokenObtainPairSerializer, RegisterSerializer, QrdataFormSerializer
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import NotFound

from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
import logging

logging.basicConfig(level=logging.DEBUG)


def home(request):
    return render(request, 'home.html', )

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
        'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                token = Token.objects.create(user=user)
                print("huiiudasd", token.key)
                login(request, user)
                # # !cambiar la url de redireccion
                # return Response({'token': token.key })
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error':  'Status: ' + str(status.HTTP_200_OK) + ' este es tu token: ' + token.key + ' guardalo en un lugar seguro ' + user.username 
                })
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Este email ya esta registrado'
                })
        
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })

@login_required
def page(request):
    return render(request, 'page.html', )

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'singin.html', {
        'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        print("huiiudasd%%%%%%%%%%%%%%%%%%%%%%", user)
        if user is None:
            return render(request, 'signup.html', {
                'form': AuthenticationForm,
                'error':  'Status: ' + str(status.HTTP_401_UNAUTHORIZED) + ' Usuario o contraseña incorrectos'
            })
        else:
            login(request, user)
            response = redirect('https://generator-web-page.vercel.app/admin')
            response.set_cookie(
                'sessionid',
                request.session.session_key,
                httponly=True,          # La cookie no será accesible desde JavaScript
                secure=True,            # La cookie solo se enviará a través de HTTPS
                samesite=None,          # Permite que las cookies se envíen en solicitudes entre sitios
                domain='.vercel.app',   # Especifica que la cookie es válida para el dominio externo
            )            
            return response

def change_password(request):
    if request.method == 'GET':
        logging.debug("GET request received.")
        return render(request, 'resetPassword.html', {
            'form': AuthenticationForm,
        })
    else:
        logging.debug("POST request received.")
        
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        logging.debug(f"email: {email}")
        logging.debug(f"new_password: {new_password}, confirm_password: {confirm_password}")
        
        if new_password != confirm_password:
            logging.error("Contraseñas no coinciden.")
            return render(request, 'resetPassword.html', {
                'form': AuthenticationForm,
                'error': 'Contraseñas no coinciden',
            })
        
        # Authenticate the user
        # user = authenticate(request, username=email, password=current_password)
        # if user is None:
        #     logging.error("Authentication failed. Username or email and password did not match.")
        #     return render(request, 'resetPassword.html', {
        #         'form': AuthenticationForm,
        #         'error': 'Username or email and password did not match',
        #     })
        
        try:
            user = User.objects.get(username=email)
            if user is None:
                logging.error("User not found.")
                return render(request, 'resetPassword.html', {
                    'form': AuthenticationForm,
                    'error': 'Usuario no encontrado',
                })
            user.set_password(new_password)
            user.save()

            logging.debug("Password updated successfully.")
            return render(request, 'singin.html', {
                'form': AuthenticationForm,
                'success': 'Contraseña actualizada correctamente',
            })
        except Exception as e:
            logging.error(f"An error occurred while updating the password: {e}")
            return HttpResponse(f'An error occurred while updating the password: {e}')

def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

def error_403(request, exception):
    return render(request, '403.html', status=403)


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()  # Modelo correcto
    serializer_class = TemplateSerializer  # Serializer correcto

    def retrieve(self, request, pk=None):
        """
        Obtener un único Template por su ID.
        """
        try:
            template = Template.objects.get(pk=pk)
        except Template.DoesNotExist:
            raise NotFound("Template not found.")
        
        serializer = TemplateSerializer(template)
        return Response(serializer.data)
    
    def create(self, request):
        """
        Crear un nuevo Template.
        """
        serializer = TemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def update(self, request, pk=None):
        """
        Actualizar un Template existente.
        """
        try:
            template = Template.objects.get(pk=pk)
        except Template.DoesNotExist:
            raise NotFound("Template not found.")
        
        serializer = TemplateSerializer(template, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def destroy(self, request, pk=None):
        """
        Eliminar un Template existente.
        """
        try:
            template = Template.objects.get(pk=pk)
            template.delete()
            return Response(status=204)
        except Template.DoesNotExist:
            raise NotFound("Template not found.")
        
    def list(self, request):
        """
        Listar todos los Templates.
        """
        queryset = Template.objects.all()
        serializer = TemplateSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """
        Listar todos los Templates públicos.
        """
        queryset = Template.objects.filter(hidden=False)
        serializer = TemplateSerializer(queryset, many=True)
        return Response(serializer.data)
    
class DataFormViewSet(viewsets.ModelViewSet):
    queryset = DataForm.objects.all()  # Modelo correcto
    serializer_class = DataFormSerializer  # Serializer correcto

    def retrieve(self, request, pk=None):
        """
        Obtener un único DataForm por su ID.
        """
        try:
            dataform = DataForm.objects.get(pk=pk)
        except DataForm.DoesNotExist:
            raise NotFound("DataForm not found.")
        
        serializer = DataFormSerializer(dataform)
        return Response(serializer.data)

    def create(self, request):
        """
        Crear un nuevo DataForm.
        """
        serializer = DataFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        """
        Actualizar un DataForm existente.
        """
        try:
            dataform = DataForm.objects.get(pk=pk)
        except DataForm.DoesNotExist:
            raise NotFound("DataForm not found.")
        
        serializer = DataFormSerializer(dataform, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        """
        Eliminar un DataForm existente.
        """
        try:
            dataform = DataForm.objects.get(pk=pk)
            dataform.delete()
            return Response(status=204)
        except DataForm.DoesNotExist:
            raise NotFound("DataForm not found.")

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    if request.method == 'GET':
        response = f"Hello, {request.user.username}!"
        return Response({'message': 'You are authenticated'}, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        text = request.POST.get('text')
        response = f"Hello, {request.user.username}! You sent the following text: {text}"
        return Response({'message': response}, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_400_BAD_REQUEST)

class QrCodeViewSet(viewsets.ModelViewSet):
    queryset = QrdataForm.objects.all()
    serializer_class = QrdataFormSerializer
    permission_classes = [permissions.AllowAny]