from django.contrib import admin
from .models import Template, User, DataForm, Profile, QrdataForm
admin.site.site_header = 'Dinamic Page Admin'
admin.site.site_title = 'Dinamic Page Admin'
admin.site.index_title = 'Dinamic Page Admin'

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'emailDesigner', 'namespace', 'email', 'hidden')
    readonly_fields = ('created_at', 'updated_at')

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']


class ProfileAdmin(admin.ModelAdmin):
    list_editable = ['verified']
    list_display = ['user', 'full_name' ,'verified']
class DataFormAdmin(admin.ModelAdmin):
    list_display = ('title', 'businessType', 'address', 'phone', 'email', 'created_at', 'updated_at')
    search_fields = ('title', 'businessType', 'address', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')


class QrCodeAdmin(admin.ModelAdmin):
    list_display = ('businessName', 'email', 'phone')
    search_fields = ('businessName', 'email', 'phone')


admin.site.register(Template, TemplateAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(DataForm, DataFormAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(QrdataForm, QrCodeAdmin)
# Compare this snippet from apiDinamicPage/views.py:
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm