from django.shortcuts import redirect
from django.conf import settings

from links.models import UserProjectStatistics, Project
from users.models import CustomUser


def add_session(request, id):
    project = Project.objects.get(id=id)
    user = request.user
    if user.is_authenticated:
        user.saved_projects.add(project)
    else:
        saved_param = settings.SAVED_SESSION_ID
        if request.method == 'POST':
            if request.session.get(saved_param) is None:
                request.session[saved_param] = []

        if id not in request.session[saved_param]:
            request.session[saved_param].append(id)
            request.session.modified = True

        if not UserProjectStatistics.objects.filter(
                project=project,
                user=user).exists():
            UserProjectStatistics.objects.create(project=project,
                                                 user=user)
        else:
            info = UserProjectStatistics.objects.get(project=project,
                                                     user=user)
            info.is_saved_project = True
            info.save()
    return redirect('links:project_detailed', id=id)


def delete_session(request, id):
    project = Project.objects.get(id=id)
    user = request.user
    if user.is_authenticated:
        user.saved_projects.remove(project)
    else:
        if request.session.get('saved'):
            request.session['saved'].remove(id)
            request.session.modified = True
        info = UserProjectStatistics.objects.get(project=project,
                                                 user=user,
                                                 is_saved_project=True)
        info.is_saved_project = False
        info.save()
    return redirect('links:project_detailed', id=id)
