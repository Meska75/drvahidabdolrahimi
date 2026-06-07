from django.urls import path
from . import views

app_name = "english_services"

urlpatterns = [
    path('', views.english_services_overview, name='english_services_overview'),
    path('office/', views.english_office_services, name='english_office_services'),
    path('surgery/', views.english_surgery_services, name='english_surgery_services'),
]
