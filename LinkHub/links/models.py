from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete

User = get_user_model()


class BaseClass(models.Model):
    title = models.CharField('Название', max_length=100)
    description = models.TextField('описание')
    created = models.DateTimeField('дата создания',auto_now_add=True)
    last_edit = models.DateTimeField('дата последнего редактирования', auto_now=True)

    class Meta:
        abstract = True


class Theme(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Project(BaseClass):
    theme = models.ManyToManyField(Theme,
                                   verbose_name='направления',
                                   related_name='projects',
                                   blank=True)
    main_admin = models.ForeignKey(User,
                                   on_delete=models.DO_NOTHING,
                                   verbose_name='создатель',
                                   related_name='created_projects'
                                   )
    editor = models.ManyToManyField(User,
                                    verbose_name='оедакторы',
                                    related_name='projects_edit')

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