from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('select_playlist', views.PlaylistView.select_playlist)
]