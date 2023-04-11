from django.urls import path

from . import views

app_name = 'saved'

urlpatterns = [
    path('saved/', views.add_session, name='add_session'),
    path('saved/<int:id>/add_session/', views.add_session, name='add_session'),
    path('saved/<int:id>/delete_session/', views.delete_session, name='delete_session'),
    path('saved/delete/', views.add_session, name='add_session'),
]