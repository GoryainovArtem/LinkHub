from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# class Destination(models.Model):
#     name
#     status

class BaseClass(models.Model):
    title = models.CharField('Название', max_length=100)
    description = models.TextField('описание', null=True, blank=True)
    created = models.DateTimeField('дата создания', auto_now_add=True)
    last_edit = models.DateTimeField('дата последнего редактирования', auto_now=True)

    class Meta:
        abstract = True


class Theme(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Project(BaseClass):
    ACCESS_TYPES = ((True, 'Private'), (False, 'Public'))
    GROUP_TYPES = ((True, 'Группа'), (False, 'Только я'))
    theme = models.ManyToManyField(Theme,
                                   verbose_name='направления',
                                   related_name='projects',
                                   blank=True, null=True)
    main_admin = models.ForeignKey(User,
                                   on_delete=models.DO_NOTHING,
                                   verbose_name='создатель',
                                   related_name='created_projects'
                                   )
    editor = models.ManyToManyField(User,
                                    verbose_name='Редакторы',
                                    related_name='projects_edit')

    is_private = models.BooleanField('Тип проекта', default=False,
                                     choices=ACCESS_TYPES,
                                     help_text='Укажите, кому будет доступен этот проект: '
                                               'public - доступен только создателю и редакторам; '
                                               'private - доступен для всех пользователей')
    is_group_project = models.BooleanField('Кто может работать с проектом', default=False,
                                           choices=GROUP_TYPES)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class Head(BaseClass):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='heads')

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'


class Link(BaseClass):
    url = models.URLField('ссылка')
    head = models.ForeignKey(Head,
                             on_delete=models.CASCADE,
                             related_name='links')

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'


class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'