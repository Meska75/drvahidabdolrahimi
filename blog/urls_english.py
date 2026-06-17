from django.urls import path
from . import views

app_name = 'english_blog'

urlpatterns = [
    path('', views.english_blog_list, name='english_blog_list'),
    path('<slug:slug>/', views.english_blog_detail, name='english_blog_detail'),
]
