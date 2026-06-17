from django.urls import path
from . import views

app_name = 'arabic_blog'

urlpatterns = [
    path('', views.arabic_blog_list, name='arabic_blog_list'),
    path('<slug:slug>/', views.arabic_blog_detail, name='arabic_blog_detail'),
]
