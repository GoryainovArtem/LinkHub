import logging
from datetime import timedelta

import pandas as pd
from random import sample

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from sklearn.preprocessing import MultiLabelBinarizer


from django.conf import settings
from django.db.models import Q
from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView, DeleteView

from .mixins import HeadAuthorRequiredMixin, AuthorRequiredMixin, LinkAuthorRequiredMixin, \
    ProjectAuthorRequiredMixin
from .models import Project, Head, Link, Comment, Theme, ProxyProjectOrderedDesc, \
    ProxyProjectOrderedStars, UserProjectStatistics
from .forms import ProjectForm, LinkForm, \
    CreateHeadForm, SearchForm, CommentForm, \
    GiveEditorRoleForm
from .utils import log_user_activity

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

        request_params = dict(self.request.GET)
        if 'page' in request_params:
            return super().get(request, *args, **kwargs)
        if request_params != self.request.session.get('selected_filters'):
            self.request.session['selected_filters'] = request_params
            self.request.modified = True
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Index, self).get_context_data()
        context['search_form'] = SearchForm()
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context

    def get_queryset(self):
        if self.request.session.get('selected_filters'):
            request_params = self.request.session['selected_filters']
            sorted_type = request_params.get('sorted_type', '0')[0]
            project_model = self.PROJECTS_LIST_MODEL[sorted_type]
            themes = request_params.get('theme')
            queryset = project_model.objects.filter(is_private=False)
            if themes:
                for theme in themes:
                    queryset = queryset.filter(theme__in=theme)
            return queryset
        return self.queryset

    def get_themes(self):
        return Theme.objects.all()


class DetailedProject(DetailView):
    model = Project
    template_name = 'links/project_detail.html'
    pk_url_kwarg = 'id'
    context_object_name = 'project'

    def __get_project(self):
        return get_object_or_404(
            Project,
            id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        log_user_activity(project=self.__get_project(),
                          user=self.request.user)
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
            context['is_liked'] = self.request.user in project.liked_users.all()
            context['is_saved'] = project in self.request.user.saved_projects.all()
        else:
            session = self.request.session.get(settings.SAVED_SESSION_ID)
            if session:
                context['is_saved'] = project.id in session
        return context


class CreateProject(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'links/create_project.html'
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.main_admin = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('links:project_detailed', kwargs={'id': self.object.id})


class RecentProjects(LoginRequiredMixin, ListView):
    """
    Получить список из 5 проектов, которые были изменены пользователем в течении
    последних 3х дней.
    """
    RECENTLY_EDIT_PROJECTS_AMOUNT = 5
    model = Project
    template_name = 'links/recent.html'
    context_object_name = 'projects'

    def __check_project_edit(self, project):
        if project.last_edit > timezone.now() - timedelta(days=3):
            return True
        for head in project.heads.all():
            if head.last_edit > timezone.now() - timedelta(days=3):
                return True
            for link in head.links.all():
                if link.last_edit > timezone.now() - timedelta(days=3):
                    return True
        return False

    def __get_page_content(self):
        user = self.request.user
        edited_projects_list = []
        criterions = Q(main_admin=user) | Q(editor=user)
        for project in Project.objects.filter(criterions):
            if self.__check_project_edit(project):
                edited_projects_list.append(project)
        return edited_projects_list

    def get_context_data(self, *, object_list=None, **kwargs):
        content = super().get_context_data()
        content['have_content'] = self.__get_page_content()
        content['page_title'] = 'Проекты, с которыми вы недавно работали:'
        return content

    def get_queryset(self):
        return self.__get_page_content()


class LikeProject(LoginRequiredMixin, View):
    """Поставить проекту отметку 'Мне нравится'"""

    def post(self, request, *args, **kwargs):
        user = self.request.user
        project = get_object_or_404(Project, id=kwargs['id'])
        project.liked_users.add(user)
        return redirect('links:project_detailed', id=kwargs['id'])


class DenyLike(LoginRequiredMixin, View):
    """Убрать у проекта отметку 'Мне нравится'."""

    def post(self, request, *args, **kwargs):
        user = request.user
        project = get_object_or_404(Project, id=kwargs['id'])
        project.liked_users.remove(user)
        return redirect('links:project_detailed', id=kwargs['id'])


class DetailedHead(DetailView):
    """Класс для раздела проекта."""
    model = Head
    template_name = 'links/heads.html'
    pk_url_kwarg = 'id'
    context_object_name = 'head'

    def get_context_data(self, **kwargs):
        head = get_object_or_404(Head, id=self.kwargs['id'])
        log_user_activity(head.project, self.request.user)
        context = super().get_context_data()
        context['is_author'] = (self.request.user == head.project.main_admin or
                                self.request.user == head.project.editor)
        return context


class HeadEdit(HeadAuthorRequiredMixin, UpdateView):
    """Редактирование информации о разделе."""
    model = Head
    form_class = CreateHeadForm
    template_name = 'links/create_head.html'
    pk_url_kwarg = 'head_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['is_editing'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('links:project_detailed',
                            kwargs={'id': self.object.project.id})


class LinkDetailed(DetailView):
    """Подробное описание источника информации."""
    template_name = 'links/link_detail.html'
    model = Link
    pk_url_kwarg = 'id'
    context_object_name = 'link'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        link = get_object_or_404(Link, id=self.kwargs['id'])
        context['comments'] = link.comments.select_related('author')
        context['form'] = CommentForm()
        project = link.head.project
        log_user_activity(project, self.request.user)
        return context


class CreateLink(LoginRequiredMixin, CreateView):
    """Создать источник информации."""
    model = Link
    template_name = 'links/create_link.html'
    form_class = LinkForm
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        head = get_object_or_404(Head, id=self.kwargs.get('id'))
        form.instance.head = head
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('links:head',
                            kwargs={
                                'id': self.kwargs.get('id')})


class CreateHead(LoginRequiredMixin, CreateView):
    model = Head
    template_name = 'links/create_head.html'
    form_class = CreateHeadForm
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        project = get_object_or_404(Project, id=self.kwargs.get('id'))
        form.instance.project = project
        return super().form_valid(form)

    def get_success_url(self):
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
        if self.request.user == user:
            context['projects'] = ProxyProjectOrderedStars.objects.filter(search_criterions).distinct()
        else:
            context['projects'] = ProxyProjectOrderedStars.objects.filter(search_criterions).filter(
                is_private=False
            )
        return context


class InterestList(ListView):
    model = Project
    template_name = 'links/interest_list.html'
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        theme = get_object_or_404(Theme, id=self.kwargs['pk'])
        context['theme'] = theme
        return context

    def get_queryset(self):
        return Project.objects.filter(theme__id=self.kwargs['pk'])


class EditProfile(AuthorRequiredMixin, UpdateView):
    model = CustomUser
    form_class = EditProfileForm
    template_name = 'links/edit_profile.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('links:profile', args=(self.object.id, ))


class ProjectEdit(ProjectAuthorRequiredMixin, UpdateView):
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


class LinkDelete(LinkAuthorRequiredMixin, DeleteView):
    model = Link
    template_name = 'links/delete_confirm.html'
    pk_url_kwarg = 'link_id'

    def get_success_url(self):
        return reverse_lazy('links:head',
                            kwargs={
                                'id': self.object.head.id
                            }
                            )


class LinkEdit(LinkAuthorRequiredMixin, UpdateView):
    model = Link
    form_class = LinkForm
    template_name = 'links/create_link.html'
    pk_url_kwarg = 'link_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['is_editing'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('links:head',
                            kwargs={
                                'id': self.object.head.id})


class AddComment(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        text = request.POST.get('text')
        user = request.user
        link = get_object_or_404(Link, id=kwargs['id'])
        Comment.objects.create(author=user,
                               text=text,
                               link=link
                               )

        return redirect('links:link', id=kwargs['id'])


class SavedProjects(ListView):
    template_name = 'links/recent.html'
    model = Project
    context_object_name = 'projects'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        if self.request.user.is_authenticated:
            context['have_content'] = self.request.user.saved_projects.all()
        else:
            context['have_content'] = self.request.session.get(settings.SAVED_SESSION_ID)
        context['page_title'] = 'Сохраненные'
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.saved_projects.all()
        saved_list = self.request.session.get(settings.SAVED_SESSION_ID, [])
        return Project.objects.filter(id__in=saved_list)


class Feed(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'links/recent.html'
    page_kwarg = 'id'
    context_object_name = 'projects'

    def get_context_data(self, *, object_list=None, **kwargs):
        content = super().get_context_data()
        content['have_content'] = True
        return content

    def get_queryset(self):

        LIMIT_PAGE_VISIT_NUMBER = 25

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
            themes_list = [{'themes': list(Project.objects.get(id=id).theme.all().values_list('name', flat=True))} for id in project_id_list]
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
            RECOMMEND_PROJECTS_AMOUNT = 2

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
            top_projects = list(random_projects_df.nlargest(RECOMMEND_PROJECTS_AMOUNT, 'avg_corr').id.values)
            return top_projects

        user_projects_criterions = Q(user=self.request.user) & (
                Q(is_created_project=True) |
                Q(is_liked_project=True) |
                Q(is_saved_project=True) |
                (Q(views_amount__gt=LIMIT_PAGE_VISIT_NUMBER))
                & Q(last_visit_date__gte=timezone.now() - timedelta(days=2)))
        us = UserProjectStatistics.objects.filter(user_projects_criterions)
        project_ids = us.filter().values_list('project', flat=True)
        if us.count() < 0:
            return ProxyProjectOrderedStars.objects.all().exclude(id__in=us.values_list('project'))
        else:
            user_projects = form_projects_dataset(project_ids)
            random_projects_id_list = get_id_random_projects()
            random_projects = form_projects_dataset(random_projects_id_list, is_random=True)
            top_projects = analise_projects(user_projects, random_projects)
            return Project.objects.filter(id__in=top_projects)


class GiveEditorRole(LoginRequiredMixin, View):
    """Назначить пользователя редактором проекта"""

    def get(self, request, *args, **kwargs):
        user = request.user
        template = 'links/give_editor_role.html'
        editor = get_object_or_404(CustomUser, id=kwargs['editor_id'])
        form = GiveEditorRoleForm()
        form.fields['id'] = forms.ModelChoiceField(
            queryset=Project.objects.filter(main_admin=user).exclude(editor=editor),
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


class DenyEditorRole(LoginRequiredMixin, View):
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


class HeadDelete(HeadAuthorRequiredMixin, DeleteView):
    model = Head
    template_name = 'links/delete_confirm.html'
    pk_url_kwarg = 'head_id'

    def get_success_url(self):
        return reverse_lazy('links:project_detailed',
                            kwargs={
                                'id': self.object.project.id
                            }
                            )
