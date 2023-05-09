from django.shortcuts import redirect
from django.conf import settings

from links.models import UserProjectStatistics, Project


def add_session(request, id):
    print(request.session.get(settings.SAVED_SESSION_ID))
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
    return redirect('links:project_detailed', id=id)
