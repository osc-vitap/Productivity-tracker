from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('focus_mode/', views.about, name='focus_mode'),
    path('tracker/', views.activity_tracks, name='tracker'),
    path('resetTracker/', views.resetTracker, name='resetTracker'),
    path('setTime', views.setTime, name='setTime'),
    path('setTime', views.setTime, name='setTime'),
    path("about/", views.about_page, name="about"),
]
