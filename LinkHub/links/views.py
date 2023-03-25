from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    template = 'links/project_page.html'
    return render(request, template)
