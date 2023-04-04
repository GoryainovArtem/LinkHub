from django.contrib import admin
from .models import Project, Theme, Head, Link, Comment, Star
from .forms import CreateLinkAdminForm


class CustomProject(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'created', 'last_edit', 'is_private', 'is_group_project')
    list_filter = ('created',)
    list_editable = ('title', 'description', 'is_private', 'is_group_project')


class CustomHead(admin.ModelAdmin):
    list_display = ('id', 'title', 'number', 'description', 'project', 'created', 'last_edit')
    list_filter = ('created',)
    list_editable = ('title', 'description', )


class CustomTheme(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


class CustomLink(admin.ModelAdmin):
    list_display = ('id', 'title', 'number', 'description', 'url', 'head')
    list_editable = ('title', 'title', 'number', 'description', 'url')
    form = CreateLinkAdminForm


class CustomComment(admin.ModelAdmin):
    list_display = ('id', 'text', 'created', 'author', 'link')
    list_editable = ('text', )


class CustomStar(admin.ModelAdmin):
    list_display = ('id', 'project', 'liked')


admin.site.register(Star, CustomStar)
admin.site.register(Comment, CustomComment)
admin.site.register(Link, CustomLink)
admin.site.register(Project, CustomProject)
admin.site.register(Theme, CustomTheme)
admin.site.register(Head, CustomHead)
