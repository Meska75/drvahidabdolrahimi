from django.urls import path
from . import views

app_name = "arabic"

urlpatterns = [
    path('', views.arabic_home, name='arabic_home'),
    path('about/', views.arabic_about, name='arabic_about'),
    path('contact/', views.arabic_contact, name='arabic_contact'),
    path('faq/', views.arabic_faq, name='arabic_faq'),
]