from django.urls import path
from . import views

app_name = "english"

urlpatterns = [
    path('', views.english_home, name='english_home'),
    path('about/', views.english_about, name='english_about'),
    path('contact/', views.english_contact, name='english_contact'),
    path('faq/', views.english_faq, name='english_faq'),
    path('search/', views.english_search, name='english_search'),
]
