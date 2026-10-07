from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('config/', views.widget_config, name='config'),
    path('start/', views.start_chat, name='start'),
    path('message/', views.send_message, name='message'),
    path('stream/', views.stream_message, name='stream'),
    path('clear/', views.clear_chat, name='clear'),
]
