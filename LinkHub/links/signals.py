import re
from bs4 import BeautifulSoup

from django.db.models import Max, Sum, Q
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save, post_delete, pre_save, m2m_changed
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404

from .models import Head, Project, Link, UserProjectStatistics, Star
from users.models import CustomUser


@receiver(pre_delete, sender=CustomUser)
def set_editor_as_main_admin(**kwargs):
    deleted_user = kwargs.get('instance')
    all_projects = deleted_user.created_projects.prefetch_related('editor')
    for project in all_projects:
        new_admin = min(project.editor.all(), key=lambda x: x.date_joined)
        project.main_admin = new_admin
        project.save()


def count_text_percentage(s):
    soup = BeautifulSoup(s, features="html.parser")
    text = soup.get_text()
    text = ''.join(text.split())
    if text:
        return len(text), len(s)
    else:
        return 0, 0


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
def count_image_percentage(lst):
    has_image_list = [find_image(i) for i in lst]
    return sum(has_image_list) / len(has_image_list)


# # Для видео
def count_video_percentage(lst):
    has_video_list = [find_youtube_video(link) for link in lst]
    return sum(has_video_list) / len(has_video_list)


@receiver(signal=post_save, sender=Project)
def create_user_project_statics(sender, instance, created, **kwargs):
    if created:
        user = instance.main_admin
        UserProjectStatistics.objects.create(project=instance, user=user,
                                             is_created_project=True)


@receiver(m2m_changed, sender=Project.editor.through)
def my_m2m_changed_receiver(sender, instance, action, **kwargs):
    if action == 'post_add':
        print('New objects were added to the ManyToMany field')
        print('Сущность', kwargs['pk_set'])
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
    project = instance.head.project
    links = Link.objects.filter(head__project=project)
    try:
        old_instance = Link.objects.get(id=instance.id)
    except:
        old_instance = None
    project.source_amount = project.heads.values_list('links').count() + bool(not old_instance)
    print('Старье:', old_instance)
    if old_instance is None:
        print('Description was changed')
        links_descriptions = list(links.values_list('description', flat=True))
        # links_descriptions.remove(old_instance.description)
        links_descriptions.append(instance.description)
        project.image_percentage = count_image_percentage(links_descriptions)
        project.video_percentage = count_video_percentage(links_descriptions)

        text_percentage_list = [count_text_percentage(link) for link in links_descriptions]
        project.text_percentage = (sum(map(lambda x: x[0], text_percentage_list)) /
                                   sum(map(lambda x: x[1], text_percentage_list))
                                   )

        links_urls = list(links.values_list('url', flat=True))
        links_urls.append(instance.url)
        filtered_links_urls = list(filter(None, links_urls))
        if len(links_urls) == 0:
            project.links_percentage = 0
        else:
            project.links_percentage = len(filtered_links_urls) / len(links_urls)

        print('Document was changed')
        links_documents = links.values_list('document', flat=True)
        filtered_links_documents = list(filter(None, links_documents))
        if len(links_documents) == 0:
            project.links_documents = 0
        else:
            project.links_documents = len(filtered_links_documents) / len(links_documents)

        project.stars_amount = project.stars.count()
        print('Количество звезд:', project.stars.count())
    project.save()
    # else:
    #     if old_instance.description != instance.description:
    #         print('Description was changed')
    #         links_descriptions = links.values_list('description', flat=True)
    #         # links_descriptions.remove(old_instance.description)
    #         # links_descriptions.append(instance.description)
    #         project.image_percentage = count_image_percentage(links_descriptions)
    #         project.video_percentage = count_video_percentage(links_descriptions)
    #
    #         text_percentage_list = [count_text_percentage(link) for link in links_descriptions]
    #         project.text_percentage = (sum(map(lambda x: x[0], text_percentage_list)) /
    #                                    sum(map(lambda x: x[1], text_percentage_list))
    #                                    )
    #
    #     if old_instance.url != instance.url:
    #         print('Url was changed')
    #         print('Новый url', instance.url)
    #         print('Старый url', old_instance.url)
    #         links_urls = list(links.values_list('url', flat=True))
    #         print('урлы:', links_urls)
    #         links_urls.remove(old_instance.url)
    #         links_urls.append(instance.url)
    #         filtered_links_urls = list(filter(None, links_urls))
    #         print(filtered_links_urls)
    #         print(len(filtered_links_urls) / len(links_urls))
    #         project.links_percentage = len(filtered_links_urls) / len(links_urls)
    #
    #     if old_instance.document != instance.document:
    #         print('Document was changed')
    #         links_documents = links.values_list('document', flat=True)
    #         filtered_links_documents = list(filter(None, links_documents))
    #         project.links_documents = len(filtered_links_documents) / len(links_documents)
    #
    #     project.stars_amount = project.stars.count()
    #     print('Количество звезд:', project.stars.count())
    #     project.save()


    #changed_link = kwargs['instance']

    # project = changed_link.head.project
    # project.source_amount = project.heads.values_list('links').count()
    # links = Link.objects.filter(head__project=project)

    # links_descriptions = links.values_list('description', flat=True)
    # project.image_percentage = count_image_percentage(links_descriptions)
    # project.video_percentage = count_video_percentage(links_descriptions)

    # links_urls = links.values_list('url', flat=True)
    # filtered_links_urls = list(filter(None, links_urls))
    # project.links_percentage = len(filtered_links_urls) / len(links_urls)
    #
    # links_documents = links.values_list('document', flat=True)
    # filtered_links_documents = list(filter(None, links_documents))
    # project.links_documents = len(filtered_links_documents) / len(links_documents)

    # text_percentage_list = [count_text_percentage(link) for link in links_descriptions]
    # project.text_percentage = (sum(map(lambda x: x[0], text_percentage_list)) /
    #                            sum(map(lambda x: x[1], text_percentage_list))
    #                            )


@receiver(signal=post_delete, sender=Link)
def update_source_amount(**kwargs):
    link = kwargs['instance']
    project = link.head.project
    project.source_amount = project.heads.values_list('links').count()
    project.save()

#
# @receiver(pre_save, sender=Project)
# def user_created_project(sender, instance, **kwargs):
#     try:
#         old_instance = Project.objects.get(id=instance.id)
#     except:
#         old_instance = None
#
#     if old_instance is not None:
#         if old_instance.editor != instance.editor:
#             print('Старые', old_instance.editor)
#             print('Новые', instance.editor)
#             print('Поменялись редакторы')
#
#             statistic = UserProjectStatistics.objects.filter(project=instance,
#                                                              user = instance.editor)
#             statistic.is_created_project = True
#             statistic.save()
    # Если создался новый проект, то:
    # - Создать записи для админа и для редактора


@receiver(post_save, sender=Star)
def add_like_project_info(sender, instance,  **kwargs):
    """Изменить значение поля is_liked_project в модели
    UserProjectStatistics на True, если пользователь поставил
    звезду проекту"""
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
    """Изменить значение поля is_saved_project при сохранении/удалении
    проекта в закладках.
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
