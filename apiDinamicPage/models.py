from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
class Template(models.Model):
    name = models.CharField(max_length=100)
    # user = models.ForeignKey('User', on_delete=models.CASCADE)
    emailDesigner = models.CharField(default="", max_length=255)
    namespace = models.CharField(default="", max_length=100)
    email = models.EmailField(default="")
    hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def profile(self):
        profile = Profile.objects.get(user=self)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=1000)
    bio = models.CharField(max_length=100)
    image = models.ImageField(upload_to="user_images", default="default.jpg")
    image_base64 = models.TextField(blank=True, null=True, help_text="Imagen en formato base64")
    verified = models.BooleanField(default=False)



def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


class DataForm(models.Model):
    title = models.CharField(max_length=255)
    businessType = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    backgroundImage = models.TextField(blank=True)
    centralCarousel = models.JSONField(default=list)  # Establece un array vacío como default
    carouselImages = models.JSONField()
    carouselImages2 = models.JSONField()
    logo = models.TextField(blank=True)
    services = models.JSONField()
    socialLinks = models.JSONField()
    emailClient = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "apiDinamicPage_dataform"
# Compare this snippet from apiDinamicPage/views.py:


class QrdataForm(models.Model):
    qrRef = models.JSONField(default=dict, blank=True, null=True)
    generateQRCodeUrl = models.URLField(max_length=500, default="", blank=True, null=True)
    logo = models.TextField(blank=True, null=True)
    logoShape = models.CharField(max_length=50, default="square", blank=True, null=True)
    additionalImage = models.TextField(blank=True, null=True)
    fontStyle = models.CharField(max_length=100, default="Arial", blank=True, null=True)
    address = models.CharField(max_length=255, default="", blank=True, null=True)
    businessName = models.CharField(max_length=255, default="", blank=True, null=True)
    email = models.EmailField(default="", blank=True, null=True)
    phone = models.CharField(max_length=20, default="", blank=True, null=True)
    socialMedia = models.JSONField(default=dict, blank=True, null=True)
    emailClient = models.CharField(max_length=255, default="", blank=True, null=True)
    formData = models.JSONField(default=dict, blank=True, null=True)
    carouselImages = models.JSONField(default=list, blank=True, null=True)

class UserImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_images')
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Título de la imagen")
    description = models.TextField(blank=True, null=True, help_text="Descripción de la imagen")
    image = models.ImageField(upload_to="user_images", blank=True, null=True, help_text="Archivo de imagen")
    image_base64 = models.TextField(blank=True, null=True, help_text="Imagen en formato base64")
    image_type = models.CharField(max_length=50, default="png", help_text="Tipo de imagen (png, jpg, jpeg, etc.)")
    file_size = models.IntegerField(null=True, blank=True, help_text="Tamaño del archivo en bytes")
    category = models.CharField(max_length=100, default="general", help_text="Categoría de la imagen")
    is_public = models.BooleanField(default=True, help_text="Si la imagen es pública o privada")
    tags = models.JSONField(default=list, blank=True, null=True, help_text="Tags para categorizar la imagen")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "apiDinamicPage_userimage"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title or 'Sin título'}"

class ApiUrl(models.Model):
    """Modelo simple para guardar URLs de la API"""
    name = models.CharField(max_length=100, unique=True, help_text="Nombre de la URL (ej: template, user, etc.)")
    url = models.CharField(max_length=500, help_text="URL completa de la API")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "apiDinamicPage_apiurl"
        ordering = ['name']

    def __str__(self):
        return f"{self.name}: {self.url}"