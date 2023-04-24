import logging
from datetime import timedelta

import pandas as pd
from random import sample

from django.core.paginator import Paginator
from sklearn.preprocessing import MultiLabelBinarizer


from django.conf import settings
from django.db.models import Q, Count
from django import forms
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView

from .color_generator import color_generator
from .models import Project, Head, Link, Comment, Star, \
    Theme, ProxyProjectOrderedDesc, ProxyProjectOrderedStars, \
    UserProjectStatistics
from .forms import ProjectForm, LinkForm, \
    CreateHeadForm, SearchForm,  SortedProjectsType, \
    CommentForm, GiveEditorRoleForm

from users.models import CustomUser
from users.forms import EditProfileForm


class Index(ListView):
    PROJECTS_LIST_MODEL = {
        '0': Project,
        '1': ProxyProjectOrderedDesc,
        '2': ProxyProjectOrderedStars
    }
    model = Project
    template_name = 'links/index.html'
    paginate_by = 2
    queryset = Project.objects.all().filter(is_private=False)

    def get(self, request, *args, **kwargs):
        print('Сессия до', self.request.session.get('selected_filters'))
        print(self.request.GET)
        request_params = dict(self.request.GET)
        if 'page' in self.request.GET:
            print('А я тут')
            request_params.pop('page')
            if len(request_params) == 0:
                self.request.session['selected_filters'] = {}
                self.request.modified = True
            print('Параметры:', request_params)
        if not self.request.session.get('selected_filters') and request_params:
            print('Ставим')
            self.request.session['selected_filters'] = request_params
            self.request.modified = True

        print('Сессия после', self.request.session.get('selected_filters'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        print('Это get_context_data')
        context = super(Index, self).get_context_data()
        context['search_form'] = SearchForm()
        queryset = self.get_queryset()
        print('Новый quesryset', queryset)
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        print('Номер страницы', page_number)
        page_obj = paginator.get_page(page_number)
        print('Page_obj', page_obj.object_list)
        context['page_obj'] = page_obj
        return context

    def get_queryset(self):

        if self.request.session.get('selected_filters'):
            request_params = self.request.session['selected_filters']
            sorted_type = request_params.get('sorted_type', '0')[0]
            project_model = self.PROJECTS_LIST_MODEL[sorted_type]
            themes = request_params.get('theme')
            print('Параметры:', themes, project_model)
            queryset = project_model.objects.filter(is_private=False)
            for theme in themes:
                queryset = queryset.filter(theme__in=theme)
            print('Итоговый queryset', queryset)
            return queryset
        return self.queryset

        #     # if self.request.session['selected_filters']:
        #     #request_params = self.request.session['selected_filters']
        #     sorted_type = request_params.get('sorted_type', '0')
        #     project_model = self.PROJECTS_LIST_MODEL[sorted_type]
        #     themes = request_params.get('theme')
        #     print('Параметры:', themes, sorted_type)
    #     #     queryset = project_model.objects.filter(is_private=False)
    #     #     return queryset
       # return self.queryset


        # if self.request.GET.get('sorted_type') or self.request.GET.getlist('theme'):
        #     sorted_type = self.request.GET.get('sorted_type', '0')
        #     project_model = self.PROJECTS_LIST_MODEL[sorted_type]
        #     themes = self.request.GET.getlist('theme')
        #     queryset = project_model.objects.filter(is_private=False)
        #     for theme in themes:
        #         queryset = queryset.filter(theme__in=theme)
        # else:
        #     selected_filter = self.request.session.get('selected_filter')
        #     if selected_filter:
        #         queryset = self.queryset.filter()


    def get_themes(self):
        return Theme.objects.all()


class DetailedProject(DetailView):
    model = Project
    template_name = 'links/project_detail.html'
    pk_url_kwarg = 'id'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
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
        context['is_saved'] = project in self.request.user.saved_projects.all()
        context['form'] = SearchForm()
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

    def get_context_data(self, *, object_list=None, **kwargs):
        content = super().get_context_data()
        content['have_content'] = True
        content['page_title'] = 'Проекты, с которыми вы недавно работали:'
        return content

    def get_queryset(self):
        user = self.request.user
        criterions = Q(main_admin=user) | Q(editor=user)
        return Project.objects.filter(
            criterions
        ).filter(last_edit__gte=timezone.now() - timedelta(days=3)).order_by(
            '-last_edit')[:self.RECENTLY_EDIT_PROJECTS_AMOUNT]


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
    """Убрать у проекта отметку 'Мне нравится'."""

    def post(self, request, *args, **kwargs):
        user = request.user
        project = get_object_or_404(Project, id=kwargs['id'])
        star = Star.objects.get(liked=user, project=project)
        star.delete()
        return redirect('links:project_detailed', id=kwargs['id'])


class DetailedHead(DetailView):
    """Класс для раздела проекта."""
    model = Head
    template_name = 'links/heads.html'
    pk_url_kwarg = 'id'
    context_object_name = 'head'


class HeadEdit(UpdateView):
    """Редактирование информации о разделе."""
    model = Head
    form_class = CreateHeadForm
    template_name = 'links/create_head.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['is_editing'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('links:project_detailed',
                            kwargs={'id': self.object.project.id})


def link(request, id):
    """Класс для источника информации."""
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
    """Создать источник информации."""
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
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        project = get_object_or_404(Project, id=self.kwargs.get('id'))
        form.instance.project = project
        return super().form_valid(form)

    def get_success_url(self):
        print('Продолжаем')
        return reverse_lazy('links:project_detailed',
                            kwargs={'id': self.kwargs['id']})


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
        if self.request.user.is_authenticated:
            context['is_editor'] = self.request.user.created_projects.filter(editor=user)
        if self.request.user == user:
            context['projects'] = ProxyProjectOrderedStars.objects.filter(search_criterions)
            context['projects_amount'] = Project.objects.filter(
                Q(main_admin=user) | Q(editor=user)).count()
        else:
            context['projects'] = ProxyProjectOrderedStars.objects.filter(search_criterions).filter(
                is_private=False
            )
            context['projects_amount'] = (Project.objects.filter(is_private=False
                                                                 ).filter(
                Q(main_admin=user) | Q(editor=user)).count()
                    # user.created_projects.filter(is_private=False).count() +
                    #                       user.projects_edit.filter(is_private=False).count()
                                          )
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
        context['have_content'] = bool(self.request.user.saved_projects.all())
        context['page_title'] = 'Сохраненные'
        return context

    def get_queryset(self):
        return self.request.user.saved_projects.all()
        #return self.request.user.prefetch_related(saved_projects).all()
        # if self.request.session.get(settings.SAVED_SESSION_ID):
        #     saved_list = self.request.session.get(settings.SAVED_SESSION_ID)
        #     return Project.objects.filter(id__in=saved_list)


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

        def form_projects_dataset(project_id_list, is_random=False):
            """
            Сформировать набор данных по заданным id для загрузки в
            Pandas DataFrame
            :param is_random:
            :param project_id_list:
            :return:
            """
            params_names = ['main_admin', 'source_amount', 'links_percentage',
                            'image_percentage', 'video_percentage', 'document_percentage',
                            'text_percentage', 'stars_amount']
            if is_random:
                params_names.append('id')
            themes_list = [{'themes': list(Project.objects.get(id=id).theme.all())} for id in project_id_list]
            projects_params = Project.objects.filter(
                id__in=project_id_list).values(*params_names)
            for l_1, l_2 in zip(list(projects_params), themes_list):
                l_1.update(l_2)
            return projects_params

        def get_id_random_projects(random_projects_amount=2):
            """
            Подготовить случайные проекты для проверки
            пользовательской заинтересованности в них.
            :return:
            """
            projects_sample = Project.objects.all().exclude(id__in=project_ids)
            random_projects = sample(list(projects_sample), random_projects_amount)
            random_projects_id_list = list(map(lambda x: x.id, random_projects))
            return random_projects_id_list

        def analise_projects(user_projects_dataset, random_projects_dataset):
            """
            Составить рейтинг проектов в порядке убывания потенциальной
            заинтересованности пользователя
            :param random_projects_dataset:
            :param user_projects_dataset:
            :return:
            """
            user_df = pd.DataFrame(user_projects_dataset)
            random_projects_df = pd.DataFrame(random_projects_dataset)
            random_projects_id_values = random_projects_df.id.values
            random_projects_df.drop(['id'], axis=1, inplace=True)

            mlb = MultiLabelBinarizer()
            user_df = user_df.join(pd.DataFrame(mlb.fit_transform(user_df.pop('themes')),
                                                columns=mlb.classes_,
                                                index=user_df.index))
            random_projects_df = random_projects_df.join(
                pd.DataFrame(mlb.fit_transform(random_projects_df.pop('themes')),
                             columns=mlb.classes_,
                             index=random_projects_df.index))
            lst = []
            for k in range(random_projects_df.shape[0]):
                s = sum(random_projects_df.iloc[0].corr(user_df.iloc[i]) for i in range(user_df.shape[0])) / \
                    user_df.shape[0]
                lst.append(s)
            random_projects_df['avg_corr'] = lst
            random_projects_df['id'] = random_projects_id_values
            top_projects = list(random_projects_df.nlargest(2, 'avg_corr').id.values)
            return top_projects

        us = UserProjectStatistics.objects.filter(user=self.request.user)
        project_ids = us.filter().values_list('project', flat=True)
        if us.count() < 0:
            return ProxyProjectOrderedStars.objects.all().exclude(id__in=us.values_list('project'))
        else:
            user_projects = form_projects_dataset(project_ids)
            random_projects_id_list = get_id_random_projects()
            random_projects = form_projects_dataset(random_projects_id_list, is_random=True)
            top_projects = analise_projects(user_projects, random_projects)
            return Project.objects.filter(id__in=top_projects)


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


class HeadDelete(DeleteView):
    model = Head
    template_name = 'links/delete_confirm.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('links:project_detailed',
                            kwargs={
                                'id': self.object.project.id
                            }
                            )



