from django.urls import path
from . import views

app_name = 'english_gallery'

urlpatterns = [
    path('', views.english_gallery, name='english_gallery'),
]
