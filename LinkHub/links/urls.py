from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('projects/<int:id>/', views.DetailedProject.as_view(), name='project_detailed'),
    path('create-project/', views.CreateProject.as_view(), name='create_project'),
    path('profile/<str:username>/recent/', views.RecentProjects.as_view(), name='recent_projects'),
    path('projects/<int:project_id>/like/', views.LikeProject.as_view(), name='like_project'),
    path('projects/<int:project_id>/dislike/', views.deny_like, name='deny_like'),
    path('create-head', views.create_head, name='create_head'),
    path('heads/<int:head_id>/', views.head, name='head'),
    path('heads/<int:head_id>/edit/', views.head_edit, name='head_edit'),
    path('links/<int:link_id>/', views.link, name='link'),
    path('links/<int:link_id>/edit/', views.link_edit, name='link_edit'),
    path('create-link/', views.create_link, name='create_link'),
    path('profile/<int:id>/', views.profile, name='profile'),
    path('projects/<str:interest>/', views.interest, name='interest_list'),
    path('users/<int:id>/edit_profile/', views.EditProfile.as_view(), name='edit_profile')
]
