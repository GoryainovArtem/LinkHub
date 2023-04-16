import re
from bs4 import BeautifulSoup

from django.db.models import Max, Sum
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save, post_delete, pre_save
from django.forms import model_to_dict

from .models import Head, Project, Link, UserProjectStatistics
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
def create_user_project_statics(**kwargs):
    print(kwargs)
    project = kwargs['instance']
    user = project.main_admin
    UserProjectStatistics.objects.create(project=project, user=user,
                                         is_created_project=True)


@receiver(signal=pre_save, sender=Link)
def update_source_amount(sender, instance, **kwargs):
    project = instance.head.project
    project.source_amount = project.heads.values_list('links').count()
    links = Link.objects.filter(head__project=project)
    if instance.id is not None:
        old_instance = Link.objects.get(id=instance.id)
        if old_instance.description != instance.description:
            print('Description was changed')
            links_descriptions = links.values_list('description', flat=True)
            project.image_percentage = count_image_percentage(links_descriptions)
            project.video_percentage = count_video_percentage(links_descriptions)

            text_percentage_list = [count_text_percentage(link) for link in links_descriptions]
            project.text_percentage = (sum(map(lambda x: x[0], text_percentage_list)) /
                                       sum(map(lambda x: x[1], text_percentage_list))
                                       )

        if old_instance.url != instance.url:
            print('Url was changed')
            print('Новый url', instance.url)
            print('Старый url', old_instance.url)
            links_urls = links.values_list('url', flat=True)
            print('урлы:', links_urls)
            filtered_links_urls = list(filter(None, links_urls))
            print(filtered_links_urls)
            print(len(filtered_links_urls) / len(links_urls))
            project.links_percentage = len(filtered_links_urls) / len(links_urls)

        if old_instance.document != instance.document:
            print('Document was changed')
            links_documents = links.values_list('document', flat=True)
            filtered_links_documents = list(filter(None, links_documents))
            project.links_documents = len(filtered_links_documents) / len(links_documents)

        project.stars_amount = project.stars.count()
        print('Количество звезд:', project.stars.count())
        project.save()


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
