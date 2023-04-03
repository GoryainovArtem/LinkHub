from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View

from .color_generator import color_generator
from .models import Project, Head, Link, Comment, User, Star, \
    Theme, ProxyProjectOrderedDesc, ProxyProjectOrderedStars, UserProfile
from .forms import ProjectForm, LinkForm, CreateLinkForm, \
    CreateHeadForm, SearchHeadForm,  SortedProjectsType, \
    EditProfileForm


class Index(ListView):
    PROJECTS_LIST_MODEL = {
        '1': Project,
        '2': ProxyProjectOrderedDesc,
        '3': ProxyProjectOrderedStars
    }
    model = Project
    context_object_name = 'projects'
    template_name = 'links/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['form'] = SortedProjectsType()
        type_value = self.request.GET.get('type')
        if not type_value:
            project_model = Project
        else:
            project_model = self.PROJECTS_LIST_MODEL[type_value]
        context['projects'] = project_model.objects.all()
        return context

    def get_queryset(self):
        return Project.objects.all()


class DetailedProject(DetailView):
    model = Project
    template_name = 'links/project_detail.html'
    pk_url_kwarg = 'id'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        project = get_object_or_404(
            Project,
            id=self.kwargs['id'])

        if self.request.GET.get('q'):
            print('Есть запрос q')
            req_str = self.request.GET.get('q')
            context['heads'] = project.heads.filter(description__icontains=req_str)
        else:
            context['heads'] = project.heads.all()
        context['is_liked'] = project.stars.filter(
            liked=self.request.user
        ).exists()
        context['form'] = SearchHeadForm()
        return context


def create_project(request):
    template = 'links/create_project.html'
    form = ProjectForm(request.POST or None)
    context = {
        'form': form
    }
    return render(request, template, context=context)


class RecentProjects(ListView):
    model = Project
    template_name = 'links/recent.html'
    context_object_name = 'projects'


class LikeProject(View):

    def post(self, request, *args, **kwargs):
        project_id = kwargs['project_id']
        user = self.request.user
        project = get_object_or_404(Project, id=project_id)
        Star.objects.get_or_create(
            project=project,
            liked=user
        )
        return redirect('links:project_detailed', id=project_id)


def deny_like(request, project_id):
    print('Дизлайк')
    star = get_object_or_404(
        Star,
        project=project_id,
        liked = request.user
    )
    star.delete()
    return redirect('links:project_detailed', id=project_id)


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
    print('1 шаг')
    user = get_object_or_404(UserProfile, user=user)
    print('Найден')
    template = 'links/profile.html'
    context = {
        'profile': user
    }
    return render(request, template, context)


def interest(request, interest):
    theme_obj = get_object_or_404(Theme, name=interest)
    template = 'links/interest_list.html'
    projects = Project.objects.filter(theme=theme_obj)
    context = {
        'theme': theme_obj,
        'projects': projects,
    }
    return render(request, template, context)


def test(request):
    template = 'links/test_page.html'
    if request.method == 'GET':
        if request.resolver_match.view_name != 'links:test':
            print('Обнуляем')
            request.session = None
        else:
            lst = request.session.get('types', None)
    else:
        if 'types' in request.session:
            request.session['types'].append(request.POST.get('type'))
            request.session.modified = True
        else:
            request.session['types'] = [request.POST.get('type')]
    print('Список сессии:',  request.session.get('types', None))
    form = SortedProjectsType()
    type_value = request.GET.get('type')
    print('Тип:', type_value)
    context = {
        'form': form,
        'type': type_value
    }
    return render(request, template, context)


def edit_profile(request, username):
    user = get_object_or_404(UserProfile, user__username=username)
    template = 'links/edit_profile.html'
    form = EditProfileForm()
    context = {
        'form': form
    }
    return redirect('links:profile', username=username)

