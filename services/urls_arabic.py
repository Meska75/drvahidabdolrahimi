from django.urls import path
from . import views

app_name = "arabic_services"

urlpatterns = [
    path('', views.arabic_services_overview, name='arabic_services_overview'),
    path('office/', views.arabic_office_services, name='arabic_office_services'),
    path('surgery/', views.arabic_surgery_services, name='arabic_surgery_services'),
]