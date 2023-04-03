from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('project_<int:id>/', views.DetailedProject.as_view(), name='project_detailed'),
    path('create_project/', views.create_project, name='create_project'),
    path('profile_<str:username>/recent/', views.RecentProjects.as_view(), name='recent_projects'),
    path('like/project_<int:project_id>/', views.LikeProject.as_view(), name='like_project'),
    path('dislike/project_<int:project_id>/', views.deny_like, name='deny_like'),
    path('create_head', views.create_head, name='create_head'),
    path('head_<int:head_id>/', views.head, name='head'),
    path('head_<int:head_id>/edit/', views.head_edit, name='head_edit'),
    path('link_<int:link_id>/', views.link, name='link'),
    path('link_<int:link_id>/edit/', views.link_edit, name='link_edit'),
    path('create_link/', views.create_link, name='create_link'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('projects/<str:interest>/', views.interest, name='interest_list'),
    path('test/', views.test, name='test'),
    path('users/<str:username>/edit_profile/', views.edit_profile, name='edit_profile')
]
