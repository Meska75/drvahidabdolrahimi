from django.urls import path
from . import views

app_name= "persian_main"

urlpatterns = [
    path('', views.persian_home, name='persian-home'),
    path('persian_office_services', views.persian_office_services, name='persian_office_services'),
    path('persian_surgery_services', views.persian_surgery_services, name='persian_surgery_services'),
    path('persian_hperisian_contact', views.persian_hperisian_contact, name='persian_hperisian_contact'),
    path('persian_about', views.persian_about, name='persian_about'),
]