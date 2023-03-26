from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('', views.index, name='index'),
    path('project_<int:id>', views.project_detailed, name='project_detailed'),
    path('<str:theme>/', views.theme_list, name='theme_list'),
    path('create_project/', views.create_project, name='create_project'),
    path('profile_<str:username>/recent/', views.recent, name='recent_projects'),
    path('like/project_<int:>', views.like_project, name='like_project'),
    path('like/project_<int:>', views.deny_like, name='deny_like'),
]
