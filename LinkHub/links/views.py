import logging
import pandas as pd


from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django import forms
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView

from .color_generator import color_generator
from .models import Project, Head, Link, Comment, User, Star, \
    Theme, ProxyProjectOrderedDesc, ProxyProjectOrderedStars
from .forms import ProjectForm, LinkForm, \
    CreateHeadForm, SearchHeadForm,  SortedProjectsType, \
    CommentForm, GiveEditorRoleForm

from users.models import CustomUser
from users.forms import EditProfileForm


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
        if type_value is None:
            project_model = Project
        else:
            project_model = self.PROJECTS_LIST_MODEL[type_value]
        if self.request.GET.get('theme'):
            themes = list(map(int, self.request.GET.get('theme')))
            # from operator import and_
            # from functools import reduce
            # Q_list = [Q(theme=i) for i in themes]
            # project_model.objects.filter(reduce(and_, [Q(tags__name='holiday'), Q(tags__name='summer')]))
            context['projects'] = project_model.objects.filter(theme__id__in=themes)
        else:
            context['projects'] = project_model.objects.all()
        return context


class DetailedProject(DetailView):
    model = Project
    template_name = 'links/project_detail.html'
    pk_url_kwarg = 'id'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        # visited: {'page': [date, date, ...]}
        logging.basicConfig(
            level=logging.DEBUG,
            filename=f'logs/pages/{self.request.user.id}.log',
            format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
        )
        logging.debug(self.kwargs['id'])
        # print('Сессия', self.request.session['visited'])
        # print(type(self.kwargs['id']))
        # print(self.request.session['visited'].get(self.kwargs['id']))
        # if not self.request.session.get('visited'):
        #     self.request.session['visited'] = {}
        #     print('Создал словарь')
        # if not self.request.session['visited'].get(self.kwargs['id']):
        #     print('la')
        #     self.request.session['visited'][self.kwargs['id']] = []
        #     print('создал список')
        #     self.request.session.modified = True
        # else:
        #     print('не задаем список')
        # self.request.session['visited'][self.kwargs['id']].append(1)
        # self.request.session.modified = True
        # print(self.request.session['visited'])
        # print(len(self.request.session['visited'][self.kwargs['id']]))

        context = super().get_context_data()
        project = get_object_or_404(
            Project,
            id=self.kwargs['id'])

        if self.request.GET.get('q'):
            req_str = self.request.GET.get('q')
            context['heads'] = project.heads.filter(description__icontains=req_str)
        else:
            context['heads'] = project.heads.all()
        if self.request.user.is_authenticated:
            context['is_liked'] = project.stars.filter(
                liked=self.request.user
            ).exists()
        if self.request.session.get('saved'):
            context['is_saved'] = self.kwargs['id'] in self.request.session['saved']
        context['form'] = SearchHeadForm()
        return context


class CreateProject(CreateView):
    model = Project
    template_name = 'links/create_project.html'
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.main_admin = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('links:project_detailed', kwargs={'id': self.object.id})


class RecentProjects(ListView):
    RECENTLY_EDIT_PROJECTS_AMOUNT = 5
    model = Project
    template_name = 'links/recent.html'
    context_object_name = 'projects'

    def get_queryset(self):
        user = self.request.user
        criterions = Q(main_admin=user) | Q(editor=user)
        return Project.objects.filter(
            criterions
        ).order_by('-last_edit')[:self.RECENTLY_EDIT_PROJECTS_AMOUNT]


class LikeProject(View):
    """Поставить проекту отметку 'Мне нравится'"""

    def post(self, request, *args, **kwargs):
        user = self.request.user
        project = get_object_or_404(Project, id=kwargs['id'])
        Star.objects.get_or_create(
            project=project,
            liked=user
        )
        return redirect('links:project_detailed', id=kwargs['id'])


class DenyLike(View):
    """Убрать у проекта отметку 'Мне нравится'"""

    def post(self, request, *args, **kwargs):
        user = request.user
        project = get_object_or_404(Project, id=kwargs['id'])
        star = Star.objects.get(liked=user, project=project)
        star.delete()
        return redirect('links:project_detailed', id=kwargs['id'])


def head(request, id):
    template = 'links/heads.html'
    head = get_object_or_404(Head, id=id)
    context = {
        'head': head
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


def link(request, id):
    link = get_object_or_404(Link, id=id)
    comments = link.comments.select_related('author')
    print('Комменты:', comments)
    context = {
        'comments': comments,
        'link': link,
        'form': CommentForm(),
        'comments': link.comments.all()
    }
    template = 'links/link_detail.html'
    return render(request, template, context)


class CreateLink(CreateView):
    model = Link
    template_name = 'links/create_link.html'
    form_class = LinkForm
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        print('ВСЕ', self.kwargs)
        head = get_object_or_404(Head, id=self.kwargs.get('id'))
        form.instance.head = head
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('links:head',
                            kwargs={
                                'id': self.kwargs.get('id')})


class CreateHead(CreateView):
    model = Head
    template_name = 'links/create_head.html'
    form_class = CreateHeadForm
    pk_url_kwarg = 'proj_id'

    def form_valid(self, form):
        print()
        form.instance.project = self.object.prog
        return super().form_valid(form)

    def get_success_url(self):
        print('id нового раздела:', self.object)
        return reverse_lazy('links:project_detailed',
                            kwargs={'id': self.object.id})


# def create_link(request):
#     template = 'links/create_link.html'
#     form = CreateLinkForm()
#     context = {
#         'form': form
#     }
#     return render(request, template, context)


class Profile(DetailView):
    MART_ELEMENTS_AMOUNT = 3
    model = CustomUser
    template_name = 'links/profile.html'
    pk_url_kwarg = 'id'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(CustomUser, id=self.kwargs['id'])
        search_criterions = Q(main_admin=user) | Q(editor=user)
        context = super().get_context_data()
        context['mart'] = ProxyProjectOrderedStars.objects.filter(
            search_criterions)[:self.MART_ELEMENTS_AMOUNT]
        context['projects_amount'] = (user.created_projects.count() +
                                      user.projects_edit.count()
                                      )
        context['is_editor'] = self.request.user.created_projects.filter(editor=user)
        context['projects'] = ProxyProjectOrderedStars.objects.filter(search_criterions)
        return context


def interest(request, interest):
    theme_obj = get_object_or_404(Theme, name=interest)
    template = 'links/interest_list.html'
    projects = Project.objects.filter(theme=theme_obj)
    context = {
        'theme': theme_obj,
        'projects': projects,
    }
    return render(request, template, context)


class EditProfile(UpdateView):
    model = CustomUser
    form_class = EditProfileForm
    template_name = 'links/edit_profile.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        print('Такой пользователь:',
              self.object)
        return reverse_lazy('links:profile', args=(self.object.id, ))


class ProjectEdit(UpdateView):
    model = Project
    template_name = 'links/create_project.html'
    form_class = ProjectForm
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['is_editing'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('links:project_detailed',
                            kwargs={
                                'id': self.object.id})


class LinkDelete(DeleteView):
    model = Link
    template_name = 'links/delete_confirm.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('links:head',
                            kwargs={
                                'id': self.object.head.id
                            }
                            )


class LinkEdit(UpdateView):
    model = Link
    form_class = LinkForm
    template_name = 'links/create_link.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['is_editing'] = True
        return context

    def get_success_url(self):
        print('Делаю изменение ссылки')
        return reverse_lazy('links:head',
                            kwargs={
                                'id': self.object.head.id})


class AddComment(View):
    def post(self, request, *args, **kwargs):
        text = request.POST.get('text')
        user = request.user
        link = get_object_or_404(Link, id=kwargs['id'])
        Comment.objects.create(author=user,
                               text=text,
                               link=link
                               )

        return redirect('links:link', id=kwargs['id'])


class LikedProjects(ListView):
    template_name = 'links/recent.html'
    model = Star
    context_object_name = 'projects'

    def get_queryset(self):
        print('Проекты:',  Star.objects.filter(liked=self.request.user))
        return Project.objects.filter(stars__liked=self.request.user)


class SavedProjects(ListView):
    template_name = 'links/recent.html'
    model = Project
    context_object_name = 'projects'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['have_content'] = self.request.session.get('saved')
        context['page_title'] = 'Сохраненные'
        return context

    def get_queryset(self):
        if self.request.session.get('saved'):
            saved_list = self.request.session.get('saved')
            return Project.objects.filter(id__in=saved_list)


class Feed(ListView):
    model = Project
    template_name = 'links/recent.html'
    page_kwarg = 'id'
    context_object_name = 'projects'

    def get_context_data(self, *, object_list=None, **kwargs):
        content = super().get_context_data()
        content['have_content'] = True
        return content

    def get_queryset(self):
        #  -- Мои проекты --
        # Темы
        # Есть ли картинки у большинства постов
        # Есть ли видео у большинства постов
        # Сколько источников
        # Есть ли ссылка
        # Есть ли документ

        my_projects = Project.objects.filter(
            Q(main_admin=self.request.user) | Q(editor=self.request.user)
        )

        created_themes_list = my_projects.values_list('theme', flat=True)
        print('Созданные темы:', list(created_themes_list))

        # Темы
        def find_most_appear_themes(lst):
            data = list(map(lambda x: (x, lst.count(x)), set(lst)))
            data.sort(key=lambda x: x[1])
            return list(map(lambda x: x[0], data))[:3]

        my_themes_list = find_most_appear_themes(list(created_themes_list))

        # Картинки и видео
        import re
        links = Link.objects.filter(head__project__id__in=my_projects.values_list('id', flat=True))
        created_links_list = list(links.values_list('description', flat=True))

        def closure(pattern):
            def wrapper(s):
                search_result = re.findall(pattern, s)
                return bool(search_result)
            return wrapper

        image_pattern = r'<img'
        video_pattern = r'<iframe'
        find_image = closure(image_pattern)
        find_youtube_video = closure(video_pattern)

        # Для изображения
        def image_in_half(lst):
            has_image_list = [find_image(i) for i in lst]
            return sum(has_image_list) >= len(has_image_list) / 2

        # # Для видео
        def video_in_half(lst):
            has_video_list = [find_youtube_video(link) for link in lst]
            return sum(has_video_list) >= len(has_video_list) / 2

        created_image_flag = image_in_half(created_links_list)
        created_video_flag = video_in_half(created_links_list)

        # Источники
        links_amount = [project.heads.aggregate(Count('links')) for project in my_projects ]
        print(links_amount)

        def links_amount_feature(lst):
            links_amount = [project.heads.aggregate(Count('links')) for project in my_projects ]
            return sum(links_amount) / len(links_amount)

        # есть ссылка?
        created_links_list = list(links.values_list('url', flat=True))
        def url_in_half(lst):
            has_video_list = [find_youtube_video(link) for link in lst]
            return sum(has_video_list) >= len(has_video_list) / 2
        #links.values_list('url', flat=True)

        # есть документ?
        #links.values_list('document', flat=True)


        # # Оцененные
        liked_projects = Project.objects.filter(stars__liked=self.request.user)

        # Темы
        liked_themes_list = liked_projects.values_list('theme', flat=True)
        liked_themes_list = find_most_appear_themes(list(liked_themes_list))

        # Для изображения
        links = Link.objects.filter(head__project__id__in=liked_projects.values_list('id', flat=True))
        liked_links_list = list(links.values_list('description', flat=True))
        print('Оцененные ссылки', liked_links_list, sep='\n')

        liked_image_flag = image_in_half(liked_links_list)
        liked_video_flag = video_in_half(liked_links_list)


        # Источники

        # Есть ссылка?

        # Есть документ?


        ## Сохраненные
        if not self.request.session.get('saved'):
            saved_themes_list = []
            saved_image_flag = False
            saved_video_flag = False
        else:
            saved_projects_id = self.request.session['saved']
            saved_projects = Project.objects.filter(id__in=saved_projects_id)


            ## Темы
            saved_themes_list = saved_projects.values_list('theme', flat=True)
            saved_themes_list = find_most_appear_themes(list(saved_themes_list))

            # Изображение и видео
            links = Link.objects.filter(id__in=saved_projects_id)
            saved_links_list = links.values_list('description', flat=True)

            saved_image_flag = image_in_half(saved_links_list)
            saved_video_flag = video_in_half(saved_links_list)

            # Авторы
            # Star.objects.filter(liked=user).values_list('project', flat=True) <- id проектов, которые лайкнул пользователь

        # # Просмотренные страницы
        import re
        import pandas as pd
        with open('D:/Dev/LinkHub/LinkHub/logs/pages/2.log') as file:
            pattern = r'., DEBUG,'
            data = [line.strip('\n') for line in file.readlines()]
            data = [line for line in data if re.search(pattern, line)]
            print(*data, sep='\n')

            data = list(map(lambda x: x.split(', '), data))
            data = [i for i in data if i[2] == 'root']
            df = pd.DataFrame(data, columns=['date', 'level', 'user', 'project_id'])
            res = df.groupby(by='project_id').date.count().nlargest(2)
            watched_projects_ids = list(map(int, res.keys()))

        watched_list = Project.objects.filter(id__in=watched_projects_ids)
        watched_themes_list = watched_list.values_list('theme', flat=True)
        watched_themes_list = find_most_appear_themes(list(watched_themes_list))

        links = Link.objects.filter(id__in=watched_projects_ids)
        watched_links_list = links.values_list('description', flat=True)

        watched_image_flag = image_in_half(watched_links_list)
        watched_video_flag = video_in_half(watched_links_list)


        def count_coef(flag_values, coefs):
            return sum(flag * coef for flag, coef in zip(flag_values, coefs))


        image_flags = (created_image_flag, liked_image_flag,  saved_image_flag,
                       watched_image_flag)
        IMAGE_COEFFICIENTS = (1.75, 1.25, 0.8, 0.5)

        image_coef = count_coef(image_flags, IMAGE_COEFFICIENTS)


        video_flags = (created_video_flag, liked_video_flag,  saved_video_flag,
                       watched_video_flag)
        VIDEO_COEFFICIENTS = (1.75, 1.25, 0.8, 0.5)

        video_coef = count_coef(video_flags, VIDEO_COEFFICIENTS)








        def add_coefficients(my_projects_list, liked_projects_list,
                             saved_projects_list, watched_project_list):
            my_project_coef = 3
            liked_project_coef = 1.5
            saved_project_coef = 1
            watched_project_coef = 0.75
            my_project_coefs_list = [my_project_coef] * len(my_projects_list)
            liked_project_coefs_list = [liked_project_coef] * len(liked_projects_list)
            saved_project_coefs_list = [saved_project_coef] * len(saved_projects_list)
            watched_project_coefs_list = [watched_project_coef] * len(watched_project_list)
            return (list(zip(my_projects_list, my_project_coefs_list)) +
                    list(zip(liked_projects_list, liked_project_coefs_list)) +
                    list(zip(saved_projects_list, saved_project_coefs_list)) +
                    list(zip(watched_project_list, watched_project_coefs_list)))

        themes_with_coefs = add_coefficients(created_themes_list,
                                             liked_themes_list,
                                             saved_themes_list,
                                             watched_themes_list
                                             )
        tags_coefficients = {}
        for i in themes_with_coefs:
            tags_coefficients.setdefault(i[0], 0)
            tags_coefficients[i[0]] += i[1]
        print(tags_coefficients)


        from random import sample

        random_projects = sample(list(Project.objects.all()), 2)

        def count_rating(project):
            themes_coefs = sum(tags_coefficients[theme.id] for theme in project.theme.all())
            print('Флаги картинок', image_flags)
            links = Link.objects.filter(id__in=saved_projects_id)
            links_list = links.values_list('description', flat=True)

            image_flag = image_in_half(links_list)
            video_flag = video_in_half(links_list)
            return themes_coefs + image_flag * image_coef + video_flag * video_coef

        print('Коэффициенты:', tags_coefficients)
        random_projects.sort(key=count_rating, reverse=True)
        print('Итоговые проекты:', random_projects)
        return random_projects


class GiveEditorRole(View):
    """Назначить пользователя редактором проекта"""

    def get(self, request, *args, **kwargs):
        user = request.user
        template = 'links/give_editor_role.html'
        editor = get_object_or_404(CustomUser, id=kwargs['editor_id'])
        form = GiveEditorRoleForm()
        form.fields['id'] = forms.ModelChoiceField(
            queryset=Project.objects.filter(main_admin=user),
            label='Проект',
            help_text='Выберите проект, в котором хотите выдать '
                      'роль "Редактор" данному пользователю.'
        )
        context = {
            'editor': editor,
            'form': form,
            'label_text': 'Добавить'
        }
        return render(request, template, context)

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project,
                                    id=int(request.POST.get('id'))
                                    )
        editor = get_object_or_404(CustomUser, id=kwargs['editor_id'])

        project.editor.add(editor)
        project.save()
        return redirect('links:profile', id=kwargs['editor_id'])


class DenyEditorRole(View):
    """Снять с пользователя роль редактора проекта"""
    def get(self, request, *args, **kwargs):
        editor = get_object_or_404(CustomUser, id=kwargs['editor_id'])
        template = 'links/give_editor_role.html'
        form = GiveEditorRoleForm()
        form.fields['id'] = forms.ModelChoiceField(
            queryset=Project.objects.filter(main_admin=request.user, editor=editor),
            label='Проект',
            help_text='Выберите проект, в котором хотите убрать '
                      'роль "Редактор" у данного пользователя.'
        )
        context = {
            'editor': editor,
            'form': form,
            'label_text': 'Убрать'
        }
        return render(request, template, context)

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=request.POST.get('id'))
        editor = get_object_or_404(CustomUser, id=kwargs['editor_id'])
        project.editor.remove(editor)
        project.save()
        return redirect('links:profile', kwargs['editor_id'])



