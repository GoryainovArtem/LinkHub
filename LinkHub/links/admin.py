from django.contrib import admin
from .models import Project, Theme, Head, Link, Comment, UserProjectStatistics
from .forms import AdminLinkForm, CreateAdminHeadForm, ProjectAdminForm


class CustomProject(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'created', 'last_edit', 'is_private')
    list_filter = ('created',)
    list_editable = ('title', 'description', 'is_private')
    form = ProjectAdminForm


class CustomHead(admin.ModelAdmin):
    list_display = ('id', 'title', 'number', 'description', 'project', 'created', 'last_edit')
    list_filter = ('created',)
    list_editable = ('title', 'description', )
    form = CreateAdminHeadForm


class CustomTheme(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


class CustomLink(admin.ModelAdmin):
    list_display = ('id', 'title', 'number', 'description', 'url', 'document', 'head')
    list_editable = ('title', 'title', 'number', 'description', 'url')
    form = AdminLinkForm


class CustomComment(admin.ModelAdmin):
    list_display = ('id', 'text', 'created', 'author', 'link')
    list_editable = ('text', )


class CustomUserProjectStatistics(admin.ModelAdmin):
    list_display = ('id', 'views_amount', 'is_created_project', 'is_liked_project',
                    'is_saved_project')
    list_editable = ('views_amount', 'is_created_project', 'is_liked_project',
                     'is_saved_project')


admin.site.register(UserProjectStatistics,
                    CustomUserProjectStatistics
                    )
admin.site.register(Comment, CustomComment)
admin.site.register(Link, CustomLink)
admin.site.register(Project, CustomProject)
admin.site.register(Theme, CustomTheme)
admin.site.register(Head, CustomHead)
