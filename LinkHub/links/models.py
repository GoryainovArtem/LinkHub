from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Max

User = get_user_model()

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
                                   help_text='Выберите тематику проекта')
    main_admin = models.ForeignKey(User,
                                   on_delete=models.DO_NOTHING,
                                   verbose_name='создатель',
                                   related_name='created_projects'
                                   )
    editor = models.ManyToManyField(User,
                                    verbose_name='Редакторы',
                                    related_name='projects_edit',
                                    blank=True, null=True)

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
        ordering = ('-created',)


class StarManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            stars_amount=Count('stars')
        ).order_by('-stars_amount')


class ProxyProjectOrderedDesc(Project):
    class Meta:
        proxy = True
        ordering = ('created',)


class ProxyProjectOrderedStars(Project):
    objects = StarManager()

    class Meta:
        proxy = True


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
    url = models.URLField('ссылка')
    head = models.ForeignKey(Head,
                             on_delete=models.CASCADE,
                             related_name='links')

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
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
    author = models.ForeignKey(User,
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
    liked = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name='stars')

    class Meta:
        verbose_name = 'Звезда'
        verbose_name_plural = 'Звезды'


# class UserProfile(models.Model):
#     user = models.OneToOneField(User,
#                                 on_delete=models.CASCADE
#                                 )
#     profile_image = models.ImageField(
#         'Изображение профиля',
#         upload_to='profile_image',
#         blank=True
#     )
#     about_info = models.TextField(
#         'О себе',
#         help_text='Укажите личную информацию о себе',
#         blank=True
#     )
#     first_name = models.CharField('Имя',
#                                   max_length=30,
#                                   help_text='Укажите свое имя',
#                                   blank=True)
#     last_name = models.CharField('Фамилия', max_length=40,
#                                  help_text='Укажите свою фамилию',
#                                  blank=True)
#
#     class Meta:
#         verbose_name = 'Профиль пользователя'
#         verbose_name_plural = 'Профили пользователей'

# class Follow(models.Model):
#     ...
