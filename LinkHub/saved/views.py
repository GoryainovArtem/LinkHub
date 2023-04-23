from django.shortcuts import redirect
from django.conf import settings

from links.models import UserProjectStatistics, Project


def add_session(request, id):
    print('Сессия', request.session.get('saved'))
    print(request.method)
    saved_param = settings.SAVED_SESSION_ID
    if request.method == 'POST':
        if request.session.get(saved_param) is None:
            request.session[saved_param] = []
            print('Создали')

    if id not in request.session[saved_param]:
        request.session[saved_param].append(id)
        request.session.modified = True
    project = Project.objects.get(id=id)
    user = request.user
    print('Я тут')

    if request.user.is_authenticated:
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
    print(request.session['saved'])
    if request.session.get('saved'):
        request.session['saved'].remove(id)
        request.session.modified = True
    project = Project.objects.get(id=id)
    user = request.user
    info = UserProjectStatistics.objects.get(project=project,
                                             user=user,
                                             is_saved_project=True)
    info.is_saved_project = False
    info.save()
    return redirect('links:project_detailed', id=id)
