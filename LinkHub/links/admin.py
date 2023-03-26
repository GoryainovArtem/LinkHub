from django.contrib import admin
from .models import Project, Theme, Head, Link, Comment


class CustomProject(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'created', 'last_edit', 'is_private', 'is_group_project')
    list_filter = ('created',)
    list_editable = ('title', 'description', 'is_private', 'is_group_project')


class CustomTheme(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


admin.site.register(Project, CustomProject)
admin.site.register(Theme, CustomTheme)