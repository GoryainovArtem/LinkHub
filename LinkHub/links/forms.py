from django import forms

from .models import Project, Link


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('title', 'description', 'theme',)


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ('title', 'description', 'url')