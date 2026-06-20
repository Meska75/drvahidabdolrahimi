from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
]
