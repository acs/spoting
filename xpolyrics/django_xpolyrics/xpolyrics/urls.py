from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('select_playlist', views.PlaylistView.select_playlist),
    path('select_track', views.TrackView.select_track)
]