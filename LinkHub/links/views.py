from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .color_generator import color_generator
from .models import Project, Head, Link, Comment, User
from .forms import ProjectForm, LinkForm, CreateLinkForm, CreateHeadForm


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


def like_project(request, project_id):
    pass


def deny_like(request, project_id):
    pass


def head(request, head_id):
    template = 'links/heads.html'
    head = get_object_or_404(Head, id=head_id)
    context = {
        'head': head
    }
    return render(request, template, context)


def create_head(request):
    template = 'links/create_head.html'
    form = CreateHeadForm()
    context = {
        'is_editing': False,
        'form': form
    }
    return render(request, template, context)


def head_edit(request, head_id):
    head = get_object_or_404(Head, id=head_id)
    template = 'links/create_head.html'
    form = CreateHeadForm(request.POST or None,
                          instance=head)
    context = {
        'is_editing': True,
        'form': form
    }
    return render(request, template, context)


def link(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    comments = link.comments.select_related('author')
    print('Комменты:', comments)
    context = {
        'comments': comments,
        'link': link
    }
    template = 'links/link_detail.html'
    return render(request, template, context)


def link_edit(request, link_id):
    link = get_object_or_404(Link, id=link_id)
    form = LinkForm(request.POST or None, instance=link)
    context = {
        'form': form,
        'link': link
    }
    template = 'links/link_detail.html'
    return render(request, template, context)


def create_link(request):
    template = 'links/create_link.html'
    form = CreateLinkForm()
    context = {
        'form': form
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    template = 'links/profile.html'
    context = {
        'profile': user
    }
    return render(request, template, context)
