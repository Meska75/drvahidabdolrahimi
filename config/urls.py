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
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from main.sitemaps import SITEMAPS
from config.admin_views import storage_stats_view
from main.views import paziresh24_proxy
from config.error_views import page_not_found as view_404

# هندلرهای سفارشی خطا
handler404 = 'config.error_views.page_not_found'
handler500 = 'config.error_views.server_error'

urlpatterns = [
    # بازیابی رمز عبور — باید قبل از admin.site.urls تعریف شود
    path('admin/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
         ),
         name='admin_password_reset'),
    path('admin/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html',
         ),
         name='password_reset_done'),
    path('admin/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),
    path('admin/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html',
         ),
         name='password_reset_complete'),

    # نقشه سایت و robots.txt
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain'
    ), name='robots_txt'),

    path('admin/storage-stats/', storage_stats_view, name='admin_storage_stats'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
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
    path('booking-proxy/', paziresh24_proxy, name='booking_proxy'),
]

# مسیر تست صفحه ۴۰۴ — فقط در حالت توسعه فعال است و در پروداکشن خودکار غیرفعال می‌شود
if settings.DEBUG:
    urlpatterns += [
        path('404-preview/', lambda req: view_404(req, exception=None), name='preview_404'),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)