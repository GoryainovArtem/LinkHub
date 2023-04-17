from django.shortcuts import render, redirect

from links.models import UserProjectStatistics, Project



def add_session(request, id):
    print('Сессия', request.session.get('saved'))
    print(request.method)
    if request.method == 'POST':
        if not request.session.get('saved'):
            request.session['saved'] = []

    if id not in request.session['saved']:
        request.session['saved'].append(id)
        request.session.modified = True
    project = Project.objects.get(id=id)
    user = request.user

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
