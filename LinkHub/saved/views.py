from django.shortcuts import render, redirect


def add_session(request, id):
    print('Сессия', request.session.get('saved'))
    print(request.method)
    if request.method == 'POST':
        if not request.session.get('saved'):
            request.session['saved'] = []

    if id not in request.session['saved']:
        request.session['saved'].append(id)
        request.session.modified = True
    return redirect('links:project_detailed', id=id)


def delete_session(request, id):
    print(request.session['saved'])
    if request.session.get('saved'):
        request.session['saved'].remove(id)
        request.session.modified = True
    return redirect('links:project_detailed', id=id)
