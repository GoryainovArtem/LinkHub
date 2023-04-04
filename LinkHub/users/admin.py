# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['id', 'username',
                    'first_name', 'last_name',
                    'email', 'about_info',
                    'profile_image']
    list_editable = ('first_name', 'last_name',
                     'email', 'profile_image',
                     'about_info', 'profile_image')


admin.site.register(CustomUser, CustomUserAdmin)
