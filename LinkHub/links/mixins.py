from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect, get_object_or_404

from .models import Head, Project, Link, CustomUser


class AuthorRequiredMixin(AccessMixin):
    ...


class HeadAuthorRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        else:
            head = get_object_or_404(Head, id=kwargs['head_id'])
            if head.project.main_admin != request.user or request.user not in head.project.editor.all():
                messages.info(request, 'Изменение и удаление раздела доступно только автору. '
                                       'Вы были перенаправлены на главную страницу.')
                return redirect('links:index')
        return super().dispatch(request, *args, **kwargs)


class LinkAuthorRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        else:
            link = get_object_or_404(Link, id=kwargs['link_id'])
            if link.head.project.main_admin != request.user or request.user not in link.head.project.editor.all():
                messages.info(request, 'Изменение и удаление раздела доступно только автору. '
                                       'Вы были перенаправлены на главную страницу.')
                return redirect('links:index')
        return super().dispatch(request, *args, **kwargs)


class AuthorRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        print('Параметр миксина', kwargs['username'])
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        else:
            current_user = get_object_or_404(CustomUser, id=kwargs['username'])
            if current_user != request.user:
                messages.info(request, 'Просмотр недавно измененных проектов доступен '
                                       'только автору и редакторам.')
                return redirect('links:index')
        return super().dispatch(request, *args, **kwargs)

