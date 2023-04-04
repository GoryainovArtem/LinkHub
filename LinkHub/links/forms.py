from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Project, Link, Head, Theme, \
    ProxyProjectOrderedDesc, ProxyProjectOrderedStars, \
    User

from users.models import CustomUser


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('title', 'description', 'theme',)


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ('title', 'description', 'url')


class CreateLinkForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание',
        help_text='Добавьте описание',
        widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = Link
        fields = ('title', 'description', 'url')


class CreateLinkAdminForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание',
        help_text='Добавьте описание',
        widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = Link
        fields = ('title', 'number', 'description', 'url', 'head')


class CreateHeadForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание',
        help_text='Добавьте описание',
        widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = Link
        fields = ('title', 'description')


class SearchHeadForm(forms.Form):
    input_string = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите название раздела'
            }
        )
    )


SORTED_TYPE_VALUES = (
    (1, 'новые'),
    (2, 'старые'),
    (3, 'высокий рейтинг'),
)


class SortedProjectsType(forms.ModelForm):
    type = forms.ChoiceField(choices=SORTED_TYPE_VALUES, required=False, label='Сначала показывать')
    theme = forms.ModelChoiceField(queryset=Theme.objects.all(), required=False,
                                   widget=forms.CheckboxSelectMultiple,
                                   label='Выберите тематику проекта'
    )

    class Meta:
        model = Project
        fields = ('theme', 'type', )


class EditProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description',)

