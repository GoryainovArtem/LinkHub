from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Project, Link, Head, Theme, Comment


class BaseFormWithText(forms.ModelForm):
    description = forms.CharField(
        label='Описание',
        help_text='Добавьте описание',
        widget=CKEditorUploadingWidget(), required=False)


class ProjectForm(BaseFormWithText):
    class Meta:
        model = Project
        fields = ('title', 'description', 'theme', 'is_private')


class ProjectAdminForm(BaseFormWithText):
    class Meta:
        model = Project
        fields = ('title', 'description', 'theme', 'main_admin', 'editor', 'is_private', 'source_amount',
                  'links_percentage', 'image_percentage', 'video_percentage', 'document_percentage',
                  'text_percentage', 'stars_amount')


class LinkForm(BaseFormWithText):
    class Meta:
        model = Link
        fields = ('title', 'number', 'description', 'url', 'document')


class AdminLinkForm(BaseFormWithText):
    class Meta:
        model = Link
        fields = ('title', 'number', 'description', 'url', 'head')


class CreateHeadForm(BaseFormWithText):
    class Meta:
        model = Head
        fields = ('number', 'title', 'description')


class CreateAdminHeadForm(BaseFormWithText):
    class Meta:
        model = Head
        fields = ('number', 'title', 'description', 'project')


class SearchForm(forms.Form):
    input_string = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите название проекта'
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


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Comment
        fields = ('text', )


class GiveEditorRoleForm(forms.Form):
    class Meta:
        model = Project
        fields = ('id', )

