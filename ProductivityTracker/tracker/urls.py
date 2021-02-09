from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('allapps/', views.about, name='allapps'),
    path('tracker/', views.activity_tracks, name='tracker'),
]