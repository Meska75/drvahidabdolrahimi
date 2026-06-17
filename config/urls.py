"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('main.urls')),
    path('services/', include('services.urls')),
    path('en/', include('main.urls_english')),
    path('en/services/', include('services.urls_english')),
    path('ar/', include('main.urls_arabic')),
    path('ar/services/', include('services.urls_arabic')),
    path('blog/', include('blog.urls')),
    path('en/blog/', include('blog.urls_english')),
    path('ar/blog/', include('blog.urls_arabic')),
    path('gallery/', include('gallery.urls')),
    path('en/gallery/', include('gallery.urls_english')),
    path('ar/gallery/', include('gallery.urls_arabic')),
    path('videos/', include('videos.urls')),
    path('en/videos/', include('videos.urls_english')),
    path('ar/videos/', include('videos.urls_arabic')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)