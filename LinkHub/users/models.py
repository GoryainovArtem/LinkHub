from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    profile_image = models.ImageField('Изображение профиля',
                                      upload_to='profiles',
                                      blank=True, null=True)
    first_name = models.CharField('Имя', max_length=30,
                                  blank=True, null=True
                                  )
    last_name = models.CharField('Фамилия',
                                 max_length=40,
                                 blank=True, null=True
                                 )
    about_info = models.TextField('О себе',
                                  blank=True, null=True
                                  )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'
