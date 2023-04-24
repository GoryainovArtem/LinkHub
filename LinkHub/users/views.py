from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

from .forms import SignUpForm
from links.models import Project
from users.models import CustomUser


class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')


class Login(LoginView):

    template_name = 'users/login.html'

    def form_valid(self, form):
        print('Форма:', self.request.POST)
        auth_user = get_object_or_404(
            CustomUser,
            username=self.request.POST.get('username')
        )
        if self.request.session.get('saved'):
            for saved_project_id in self.request.session.get(settings.SAVED_SESSION_ID):
                current_project = Project.objects.get(id=saved_project_id)
                if current_project not in auth_user.saved_projects.all():
                    current_project.saved_users.add(auth_user)
        return super().form_valid(form)
