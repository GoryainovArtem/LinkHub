from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Max

from users.models import CustomUser

#User = get_user_model()

# class Destination(models.Model):
#     name
#     status


class BaseClass(models.Model):
    title = models.CharField('Название',
                             max_length=100,
                             help_text='Введите название')
    description = models.TextField('описание',
                                   null=True,
                                   blank=True,
                                   help_text='Добавьте описание')
    created = models.DateTimeField('дата создания', auto_now_add=True)
    last_edit = models.DateTimeField('дата последнего редактирования', auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Theme(models.Model):
    name = models.CharField('Название', max_length=100)

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        ordering = ('name', )

    def __str__(self):
        return self.name


class Project(BaseClass):
    ACCESS_TYPES = ((True, 'Private'), (False, 'Public'))
    GROUP_TYPES = ((True, 'Группа'), (False, 'Только я'))
    theme = models.ManyToManyField(Theme,
                                   verbose_name='Тематика',
                                   related_name='projects',
                                   blank=True, null=True,
                                   help_text='Выберите тематику проекта. Для выбора нескольких значений зажмите Alt.')
    main_admin = models.ForeignKey(CustomUser,
                                   on_delete=models.DO_NOTHING,
                                   verbose_name='создатель',
                                   related_name='created_projects'
                                   )
    editor = models.ManyToManyField(CustomUser,
                                    verbose_name='Редакторы',
                                    related_name='projects_edit',
                                    blank=True, null=True,
                                    )

    is_private = models.BooleanField('Тип проекта', default=False,
                                     choices=ACCESS_TYPES,
                                     help_text='Укажите, кому будет доступен этот проект: '
                                               'public - доступен только создателю и редакторам; '
                                               'private - доступен для всех пользователей')
    is_group_project = models.BooleanField('Кто может работать с проектом', default=False,
                                           choices=GROUP_TYPES)

    source_amount = models.IntegerField(default=0)
    links_percentage = models.FloatField(default=0)
    image_percentage = models.FloatField(default=0)
    video_percentage = models.FloatField(default=0)
    document_percentage = models.FloatField(default=0)
    text_percentage = models.FloatField(default=0)
    stars_amount = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('-created',)


# class StarManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().annotate(
#             stars_amount=Count('stars')
#         ).order_by('-stars_amount')


class ProxyProjectOrderedDesc(Project):
    class Meta:
        proxy = True
        ordering = ('created',)


class ProxyProjectOrderedStars(Project):
    #objects = StarManager()

    class Meta:
        proxy = True
        ordering = ('-stars_amount', '-created')


class Head(BaseClass):
    number = models.IntegerField('Номер раздела',
                                 blank=True, null=True)
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='heads')

    class Meta:
        unique_together = ('project', 'number')
        verbose_name = 'раздел'
        verbose_name_plural = 'разделы'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.number:
            buf = self.project.heads.aggregate(max_number=Max('number'))
            print('Баф',buf)
            if buf['max_number'] is None:
                value = 1
            else:
                value = buf['max_number'] + 1
            self.number = value
        super(Head, self).save()


class Link(BaseClass):
    number = models.IntegerField(
        'номер источника', blank=True,
        null=True,
        help_text='Укажите номер источника. '
                  'Параметр необязателен и может быть выставлен автоматически')
    url = models.URLField('ссылка', blank=True, null=True)
    head = models.ForeignKey(Head,
                             on_delete=models.CASCADE,
                             related_name='links')

    document = models.FileField('Документ', blank=True, null=True,
                                upload_to='Files',
                                help_text='Выберите нужный документ')

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not (self.url or self.document or self.description):
            raise ValidationError('Хотя бы одно из полей: описание, ссылка, документ должно быть заполнено.')
        if not self.number:
            buf = self.head.links.aggregate(max_number=Max('number'))
            print('Баф',buf)
            if buf['max_number'] is None:
                value = 1
            else:
                value = buf['max_number'] + 1
            self.number = value
        super(Link, self).save()


class Comment(models.Model):
    DISPLAY_TEXT_LETTERS_AMOUNT = 15
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='comments')
    link = models.ForeignKey(Link,
                             on_delete=models.CASCADE,
                             related_name='comments')

    class Meta:
        ordering = ('-created', )
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:self.DISPLAY_TEXT_LETTERS_AMOUNT]


class Star(models.Model):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='stars')
    liked = models.ForeignKey(CustomUser,
                              on_delete=models.CASCADE,
                              related_name='stars')

    class Meta:
        verbose_name = 'Звезда'
        verbose_name_plural = 'Звезды'


class UserProjectStatistics(models.Model):
    choice_values = ((True, 'Да'), (False, 'Нет'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_statistics')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_statistics')
    is_created_project = models.BooleanField('Проект создан этим автором?', default=False,
                                             choices=choice_values)
    is_liked_project = models.BooleanField('Пользователь поставил звезду проекту?', default=False,
                                           choices=choice_values)
    is_saved_project = models.BooleanField('Пользователь добавил проект в закладки', default=False,
                                           choices=choice_values)
    views_amount = models.IntegerField('Количество просмотров проекта', default=0)

    class Meta:
        verbose_name = 'Статистика пользователя'
        verbose_name_plural = 'Статистика пользователей'
