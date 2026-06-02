from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    path('office/', views.persian_office_services, name='persian_office_services'),
    path('surgery/', views.persian_surgery_services, name='persian_surgery_services'),
]
