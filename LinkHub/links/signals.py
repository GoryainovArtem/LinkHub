from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
from .models import Project, User


@receiver(signal=post_save, sender=settings.AUTH_USER_MODEL)
def set_editor_as_main_ad(**kwargs):
    print('Сигнал работает')
    print('Параметры:', kwargs)
    #editors = Project.objects.select_related('editor').order_by('-date_joined')
    #new_creator = editors[0]
    #return new_creator


@receiver(pre_delete, sender=User)
def set_editor_as_main_admin(**kwargs):
    print('Сигнал 2 работает')
    deleted_user = kwargs.get('instance')
    all_projects = deleted_user.created_projects.all()
    print(all_projects)
    for project in all_projects:
        editors = project.editor.order_by('date_joined')
        print('Редакторы', editors)
        new_admin = editors[0]
        print(new_admin)
        project.main_admin = new_admin
        project.save()
