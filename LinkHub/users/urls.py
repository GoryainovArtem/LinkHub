from django.contrib.auth.views import LoginView
from django.urls import path
LoginView
from . import views

app_name = 'urls'


urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login')
]
