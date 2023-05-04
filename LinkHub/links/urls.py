from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('projects/<int:id>/', views.DetailedProject.as_view(), name='project_detailed'),
    path('create-project/', views.CreateProject.as_view(), name='create_project'),
    path('profile/<str:username>/recent/', views.RecentProjects.as_view(), name='recent_projects'),
    path('projects/<int:id>/like/', views.LikeProject.as_view(), name='like_project'),
    path('projects/<int:id>/dislike/', views.DenyLike.as_view(), name='deny_like'),
    path('projects/<int:id>/heads/create-head', views.CreateHead.as_view(), name='create_head'),
    path('heads/<int:id>/', views.DetailedHead.as_view(), name='head'),
    path('heads/<int:head_id>/edit/', views.HeadEdit.as_view(), name='head_edit'),
    path('heads/<int:head_id>/delete/', views.HeadDelete.as_view(), name='head_delete'),
    path('links/<int:id>/', views.link, name='link'),
    path('links/<int:link_id>/edit/', views.LinkEdit.as_view(), name='link_edit'),
    path('heads/<int:id>/create-link/', views.CreateLink.as_view(), name='create_link'),
    path('profile/<int:id>/', views.Profile.as_view(), name='profile'),
    path('interests/<int:pk>/', views.InterestList.as_view(), name='interest_list'),
    path('users/<int:id>/edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
    path('projects/<int:id>/edit/', views.ProjectEdit.as_view(), name='edit_project'),
    path('links/<int:link_id>/delete/', views.LinkDelete.as_view(), name='link_delete'),
    path('links/<int:id>/add-comment/', views.AddComment.as_view(), name='add_comment'),
    path('projects/saved/', views.SavedProjects.as_view(), name='saved_projects'),
    path('users/<int:id>/projects/feed/', views.Feed.as_view(), name='feed'),
    path('users/<int:editor_id>/give_editor_role/',
         views.GiveEditorRole.as_view(), name='give_editor_role'),
    path('users/<int:editor_id>/deny_editor_role/',
         views.DenyEditorRole.as_view(), name='deny_editor_role'),
]
