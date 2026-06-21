from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post


# ===================================================================
# اولویت هر صفحه در نقشه سایت
# ===================================================================
_PAGE_PRIORITY = {
    'home':     1.00,
    'about':    0.90,
    'services': 0.85,
    'contact':  0.70,
    'faq':      0.70,
    'gallery':  0.65,
    'videos':   0.65,
    'blog':     0.75,
}

_PAGE_CHANGEFREQ = {
    'home':     'weekly',
    'about':    'monthly',
    'services': 'monthly',
    'contact':  'yearly',
    'faq':      'monthly',
    'gallery':  'monthly',
    'videos':   'weekly',
    'blog':     'weekly',
}


# ===================================================================
# صفحات ثابت فارسی
# ===================================================================
class PersianStaticSitemap(Sitemap):
    protocol = 'https'

    _ITEMS = [
        ('main',     'persian_home',              'home'),
        ('main',     'persian_about',             'about'),
        ('main',     'persian_contact',           'contact'),
        ('main',     'persian_faq',               'faq'),
        ('services', 'persian_services_overview', 'services'),
        ('services', 'persian_office_services',   'services'),
        ('services', 'persian_surgery_services',  'services'),
        ('gallery',  'persian_gallery',           'gallery'),
        ('videos',   'persian_videos',            'videos'),
    ]

    def items(self):
        return self._ITEMS

    def priority(self, item):
        return _PAGE_PRIORITY[item[2]]

    def changefreq(self, item):
        return _PAGE_CHANGEFREQ[item[2]]

    def location(self, item):
        return reverse(f'{item[0]}:{item[1]}')


# ===================================================================
# صفحات ثابت انگلیسی
# ===================================================================
class EnglishStaticSitemap(Sitemap):
    protocol = 'https'

    _ITEMS = [
        ('english',          'english_home',              'home'),
        ('english',          'english_about',             'about'),
        ('english',          'english_contact',           'contact'),
        ('english',          'english_faq',               'faq'),
        ('english_services', 'english_services_overview', 'services'),
        ('english_services', 'english_office_services',   'services'),
        ('english_services', 'english_surgery_services',  'services'),
        ('english_gallery',  'english_gallery',           'gallery'),
        ('english_videos',   'english_videos',            'videos'),
    ]

    def items(self):
        return self._ITEMS

    def priority(self, item):
        return _PAGE_PRIORITY[item[2]]

    def changefreq(self, item):
        return _PAGE_CHANGEFREQ[item[2]]

    def location(self, item):
        return reverse(f'{item[0]}:{item[1]}')


# ===================================================================
# صفحات ثابت عربی
# ===================================================================
class ArabicStaticSitemap(Sitemap):
    protocol = 'https'

    _ITEMS = [
        ('arabic',          'arabic_home',              'home'),
        ('arabic',          'arabic_about',             'about'),
        ('arabic',          'arabic_contact',           'contact'),
        ('arabic',          'arabic_faq',               'faq'),
        ('arabic_services', 'arabic_services_overview', 'services'),
        ('arabic_services', 'arabic_office_services',   'services'),
        ('arabic_services', 'arabic_surgery_services',  'services'),
        ('arabic_gallery',  'arabic_gallery',           'gallery'),
        ('arabic_videos',   'arabic_videos',            'videos'),
    ]

    def items(self):
        return self._ITEMS

    def priority(self, item):
        return _PAGE_PRIORITY[item[2]]

    def changefreq(self, item):
        return _PAGE_CHANGEFREQ[item[2]]

    def location(self, item):
        return reverse(f'{item[0]}:{item[1]}')


# ===================================================================
# مقالات بلاگ — هر سه زبان
# ===================================================================
class BlogPersianSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = _PAGE_PRIORITY['blog']

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog:persian_blog_detail', args=[obj.slug])


class BlogEnglishSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = _PAGE_PRIORITY['blog'] - 0.05

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('english_blog:english_blog_detail', args=[obj.slug])


class BlogArabicSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'weekly'
    priority = _PAGE_PRIORITY['blog'] - 0.05

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('arabic_blog:arabic_blog_detail', args=[obj.slug])


# ===================================================================
# دیکشنری نهایی — در urls.py استفاده می‌شود
# ===================================================================
SITEMAPS = {
    'fa-static':  PersianStaticSitemap,
    'en-static':  EnglishStaticSitemap,
    'ar-static':  ArabicStaticSitemap,
    'fa-blog':    BlogPersianSitemap,
    'en-blog':    BlogEnglishSitemap,
    'ar-blog':    BlogArabicSitemap,
}
