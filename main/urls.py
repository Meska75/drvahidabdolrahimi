from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.persian_home, name='persian_home'),
    path('about/', views.persian_about, name='persian_about'),
    path('contact/', views.persian_contact, name='persian_contact'),
    path('faq/', views.persian_faq, name='persian_faq'),
    path('search/', views.persian_search, name='persian_search'),
    path('booking-proxy/', views.paziresh24_proxy, name='paziresh24_proxy'),
]
