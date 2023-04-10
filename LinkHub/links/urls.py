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
    path('projects/<int:proj_id>/heads/create-head', views.CreateHead.as_view(), name='create_head'),
    path('heads/<int:id>/', views.head, name='head'),
    path('heads/<int:head_id>/edit/', views.head_edit, name='head_edit'),
    path('links/<int:id>/', views.link, name='link'),
    path('links/<int:id>/edit/', views.LinkEdit.as_view(), name='link_edit'),
    path('heads/<int:id>/create-link/', views.CreateLink.as_view(), name='create_link'),
    path('profile/<int:id>/', views.profile, name='profile'),
    path('projects/<str:interest>/', views.interest, name='interest_list'),
    path('users/<int:id>/edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
    path('projects/<int:id>/edit/', views.ProjectEdit.as_view(), name='edit_project'),
    path('links/<int:id>/delete/', views.LinkDelete.as_view(), name='link_delete'),
    path('links/<int:id>/add-comment', views.AddComment.as_view(), name='add_comment'),
    path('users/<int:id>/projects/liked', views.LikedProjects.as_view(), name='liked_projects')
]
