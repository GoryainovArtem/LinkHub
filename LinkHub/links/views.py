from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .color_generator import color_generator
from .models import Project
from .forms import ProjectForm


def index(request):
    template = 'links/index.html'
    return render(request, template)


def project_detailed(request, id):
    project = get_object_or_404(Project, id=id)
    template = 'links/project_page.html'
    context = {
        'project': project,
    }
    return render(request, template, context)


def theme_list(request):
    return HttpResponse


def create_project(request):
    template = 'links/create_project.html'
    form = ProjectForm(request.POST or None)
    context = {
        'form': form
    }
    return render(request, template, context=context)


def recent(request, username):
    template = 'links/recent.html'
    projects = Project.objects.all()[:3]
    context = {
        'projects': projects
    }
    return render(request, template, context=context)


def like_project(request, id):
    pass


def deny_like(request, id):
    pass
