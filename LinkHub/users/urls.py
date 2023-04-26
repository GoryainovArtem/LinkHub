from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import TemplateView, View

from . import views

app_name = 'urls'

#
urlpatterns = [
    path('verification-message/',
         TemplateView.as_view(template_name='users/verification_message.html'),
         name='verification_message'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password/<uidb64>/<token>/', views.PasswordConfirm.as_view(), name='password_confirm')
]
