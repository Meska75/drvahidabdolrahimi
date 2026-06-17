from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.persian_blog_list, name='persian_blog_list'),
    path('<slug:slug>/', views.persian_blog_detail, name='persian_blog_detail'),
]
