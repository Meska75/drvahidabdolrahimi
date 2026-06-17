from django.urls import path
from . import views

app_name = 'english_videos'

urlpatterns = [
    path('', views.english_videos, name='english_videos'),
]
