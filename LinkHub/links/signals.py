import re
from bs4 import BeautifulSoup

from django.db.models import Max, Sum, Q
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save, post_delete, pre_save, m2m_changed
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404

from . import utils
from .models import Head, Project, Link, UserProjectStatistics, Star
from users.models import CustomUser


@receiver(pre_delete, sender=CustomUser)
def set_editor_as_main_admin(**kwargs):
    """
    При удалении профиля создателя проекта сделать
    новым создателем проекта редактора, который получил
    эту роль первым.
    """
    deleted_user = kwargs.get('instance')
    all_projects = deleted_user.created_projects.prefetch_related('editor')
    for project in all_projects:
        new_admin = min(project.editor.all(), key=lambda x: x.date_joined)
        project.main_admin = new_admin
        project.save()


@receiver(signal=post_save, sender=Project)
def create_user_project_statics(sender, instance, created, **kwargs):
    """
    Создать запись в таблице UserProjectStatistics со значением поля
    is_created_project=True при создании нового проекта
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        user = instance.main_admin
        UserProjectStatistics.objects.create(project=instance, user=user,
                                             is_created_project=True)


@receiver(m2m_changed, sender=Project.editor.through)
def my_m2m_changed_receiver(sender, instance, action, **kwargs):
    """
    Создать или обновить запись в таблице UserProjectStatistics со
    значением по is_created_project=True при выдачи роли редактора
    новому пользователю
    :param sender:
    :param instance:
    :param action:
    :param kwargs:
    :return:
    """
    if action == 'post_add':
        for editor_id in kwargs['pk_set']:
            editor_instance = CustomUser.objects.get(id=editor_id)
            if not UserProjectStatistics.objects.filter(
                    project=instance, user=editor_instance).exists():
                UserProjectStatistics.objects.create(project=instance, user=editor_instance,
                                                     is_created_project=True)
    elif action == 'pre_remove':
        for editor_id in kwargs['pk_set']:
            editor_instance = CustomUser.objects.get(id=editor_id)
            info = UserProjectStatistics.objects.get(project=instance,
                                                 user=editor_instance)
            info.is_created = False
            info.save()


@receiver(signal=pre_save, sender=Link)
def update_source_amount(sender, instance, **kwargs):
    """
    Изменить статистические параметры модели при добавлении или
    изменении информации об источнике.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    project = instance.head.project
    links = Link.objects.filter(head__project=project)
    try:
        old_instance = Link.objects.get(id=instance.id)
    except:
        old_instance = None
    project.source_amount = project.heads.values_list('links').count() + bool(not old_instance)
    project.stars_amount = project.stars.count()
    links_descriptions = list(links.values_list('description', flat=True))
    if old_instance is None:
        links_descriptions.append(instance.description)
        project.image_percentage = utils.count_image_percentage(links_descriptions)
        project.video_percentage = utils.count_video_percentage(links_descriptions)
        project.text_percentage = utils.get_total_text_percentage(links_descriptions)
        links_percentage = utils.get_project_statistic_field_value(links, instance, 'url')
        project.links_percentage = links_percentage
        docs_percentage = utils.get_project_statistic_field_value(links, instance, 'document')
        project.links_documents = docs_percentage
    else:
        if old_instance.description != instance.description:
            links_descriptions.remove(old_instance.description)
            links_descriptions.append(instance.description)
            project.image_percentage = utils.count_image_percentage(links_descriptions)
            project.video_percentage = utils.count_video_percentage(links_descriptions)
            project.text_percentage = utils.get_total_text_percentage(links_descriptions)
        if old_instance.url != instance.url:
            project.links_percentage = utils.get_project_statistic_field_value(links, instance, 'url')
        if old_instance.document != instance.document:
            project.links_percentage = utils.get_project_statistic_field_value(links, instance, 'document')
    project.save()


@receiver(signal=post_delete, sender=Link)
def delete_source_amount(sender, instance, **kwargs):
    """
    Изменить статистические параметры модели при удалении информации об
    источнике.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    project = instance.head.project
    project.source_amount = project.source_amount - 1
    links = Link.objects.filter(head__project=project)
    links_descriptions = list(links.values_list('description', flat=True))
    project.image_percentage = utils.count_image_percentage(links_descriptions)
    project.video_percentage = utils.count_video_percentage(links_descriptions)
    project.text_percentage = utils.get_total_text_percentage(links_descriptions)
    project.links_percentage = utils.get_project_statistic_field_value(links, instance, 'url')
    project.links_percentage = utils.get_project_statistic_field_value(links, instance, 'document')
    project.save()


@receiver(post_save, sender=Star)
def add_like_project_info(sender, instance,  **kwargs):
    """
    Изменить значение поля is_liked_project в модели
    UserProjectStatistics на True, если пользователь поставил
    звезду проекту
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    project = Project.objects.get(id=instance.project.id)
    project.stars_amount += 1
    project.save()
    if not UserProjectStatistics.objects.filter(
            project=instance.project,
            user=instance.liked).exists():
        UserProjectStatistics.objects.create(project=instance.project,
                                             user=instance.liked,
                                             is_liked_project=True)
    else:
        info = UserProjectStatistics.objects.get(project=instance.project,
                                                 user=instance.liked)
        info.is_liked_project = True
        info.save()


@receiver(pre_delete, sender=Star)
def remove_like_project_info(sender, instance, **kwargs):
    """Изменить значение поля is_liked_project в модели
    UserProjectStatistics на False, если пользователь убрал звезду у
    проекта"""
    project = Project.objects.get(id=instance.project.id)
    project.stars_amount -= 1
    project.save()
    if UserProjectStatistics.objects.filter(project=instance.project,
                                            user=instance.liked).exists():
        info = UserProjectStatistics.objects.get(project=instance.project,
                                                 user=instance.liked)
        info.is_liked_project = False
        info.save()


@receiver(m2m_changed, sender=Project.saved_users.through)
def add_save_project_info(sender, instance, action, **kwargs):
    """
    Изменить значение поля is_saved_project при сохранении/удалении
    проекта в закладках.
    :param sender:
    :param instance:
    :param action:
    :param kwargs:
    :return:
    """
    if action == 'pre_add':
        for pk in kwargs['pk_set']:
            project = get_object_or_404(Project, id=pk)
            if not UserProjectStatistics.objects.filter(project=project,
                                                        user=instance).exists():
                UserProjectStatistics.objects.create(user=instance,
                                                     project=project,
                                                     is_saved_project=True)
            else:
                info = UserProjectStatistics.objects.get(project=project,
                                                         user=instance)
                info.is_saved_project = True
                info.save()

    if action == 'pre_remove':
        for pk in kwargs['pk_set']:
            project = get_object_or_404(Project, id=pk)
            info = UserProjectStatistics.objects.get(project=project,
                                                     user=instance)
            info.is_saved_project = False
            info.save()
