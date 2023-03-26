from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_init
from .models import User, Project


@receiver(pre_delete, sender=User)
def set_editor_as_main_admin(**kwargs):
    deleted_user = kwargs.get('instance')
    all_projects = deleted_user.created_projects.prefetch_related('editor')
    for project in all_projects:
        new_admin = min(project.editor.all(), key=lambda x: x.date_joined)
        project.main_admin = new_admin
        project.save()


@receiver(pre_init, sender=Project)
def delete_main_admin_from_editors(**kwargs):
    ...
