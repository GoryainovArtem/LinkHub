from django.contrib import admin
from .models import Project, Theme, Head, Link, Comment


class CustomProject(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'created', 'last_edit', 'is_private', 'is_group_project')
    list_filter = ('created',)
    list_editable = ('title', 'description', 'is_private', 'is_group_project')


class CustomHead(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'project', 'created', 'last_edit')
    list_filter = ('created',)
    list_editable = ('title', 'description', )


class CustomTheme(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


class CustomLink(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'url')
    list_editable = ('title', 'title', 'description', 'url')


admin.site.register(Link, CustomLink)
admin.site.register(Project, CustomProject)
admin.site.register(Theme, CustomTheme)
admin.site.register(Head, CustomHead)