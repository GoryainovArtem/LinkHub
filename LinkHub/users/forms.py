from django.contrib.auth import get_user_model


User = get_user_model()

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')


class EditProfileForm(forms.ModelForm):
    about_info = forms.CharField(
        label='О себе',
        help_text='Укажите информацию о себе',
        widget=CKEditorUploadingWidget,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('profile_image',
                  'about_info',
                  'first_name',
                  'last_name')
