from django.db.models import Max
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from .models import User, Head

@receiver(pre_delete, sender=User)
def set_editor_as_main_admin(**kwargs):
    deleted_user = kwargs.get('instance')
    all_projects = deleted_user.created_projects.prefetch_related('editor')
    for project in all_projects:
        new_admin = min(project.editor.all(), key=lambda x: x.date_joined)
        project.main_admin = new_admin
        project.save()


# @receiver(post_save, sender=User)
# def create_user_profile(**kwargs):
#     """Создание записи в расширенной модели пользователя
#     при регистрации нового пользователя"""
#     print('Создан аккаунт', kwargs)
#     if kwargs.get('created'):
#         UserProfile.objects.create(user=kwargs.get('instance')
#                                    )
#
#
# # @receiver(post_save, sender=User)
# # def save_user_profile(**kwargs):
# #     kwargs['instance'].profile.save()

# @receiver(post_save, sender=Head)
# def head_number(**kwargs):
#     instance = kwargs['instance']
#     buf = instance.project.heads.aggregate(max_number=Max('number'))
#     value = buf['max_number'] + 1
#     instance.number = value
#     print('Сохраняем')
#     instance.save()
#     print('gg')
