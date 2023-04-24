from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'urls'

#
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout')
]
