from django.urls import path, include
from rest_framework import routers
from .api import TemplateViewSet, UserViewSet, DataFormViewSet, ProfileViewSet, RegisterView, TokenObtainPairView, QrCodeViewSet, UserImageViewSet, ApiUrlViewSet, VCardViewSet

# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.urls import path, include

router = routers.DefaultRouter()
router.register('template', TemplateViewSet, 'template')
router.register('user', UserViewSet, 'user')
router.register('dataform', DataFormViewSet, 'dataform')
router.register('profile', ProfileViewSet, 'profile')
router.register('register', RegisterView, 'register')
router.register('token', TokenObtainPairView, 'token')
router.register('qr', QrCodeViewSet, 'qr')
router.register('userimage', UserImageViewSet, 'userimage')
router.register('apiurls', ApiUrlViewSet, 'apiurls')
router.register('vcard', VCardViewSet, 'vcard')

# rutas para el servicio de QR
# rutas para el templateDinamic y el templateDinamicData



urlpatterns = router.urls