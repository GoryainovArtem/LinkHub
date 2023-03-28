from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Project, Link


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


class CreateHeadForm(forms.ModelForm):
    description = forms.CharField(
        label='Описание',
        help_text='Добавьте описание',
        widget=CKEditorUploadingWidget(), required=False)

    class Meta:
        model = Link
        fields = ('title', 'description')
