from django.urls import path
from . import views

app_name = 'arabic_videos'

urlpatterns = [
    path('', views.arabic_videos, name='arabic_videos'),
]
