from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('', views.index, name='index'),
    path('project_<int:id>/', views.project_detailed, name='project_detailed'),
    path('create_project/', views.create_project, name='create_project'),
    path('profile_<str:username>/recent/', views.recent, name='recent_projects'),
    path('like/project_<int:project_id>/', views.like_project, name='like_project'),
    path('like/project_<int:project_id>/', views.deny_like, name='deny_like'),
    path('create_head', views.create_head, name='create_head'),
    path('head_<int:head_id>/', views.head, name='head'),
    path('head_<int:head_id>/edit/', views.head_edit, name='head_edit'),
    path('link_<int:link_id>/', views.link, name='link'),
    path('link_<int:link_id>/edit/', views.link_edit, name='link_edit'),
    path('create_link/', views.create_link, name='create_link')
]
