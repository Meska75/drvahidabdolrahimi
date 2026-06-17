from django.urls import path
from . import views

app_name = 'arabic_gallery'

urlpatterns = [
    path('', views.arabic_gallery, name='arabic_gallery'),
]
