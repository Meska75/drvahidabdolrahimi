from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from utils.image_validators import validate_image_size, validate_video_size


class VideoCategory(models.Model):
    name_fa = models.CharField(max_length=100, verbose_name='نام فارسی')
    name_en = models.CharField(max_length=100, blank=True, verbose_name='English Name')
    name_ar = models.CharField(max_length=100, blank=True, verbose_name='الاسم العربي')
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name='اسلاگ')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'دسته‌بندی ویدیو'
        verbose_name_plural = 'دسته‌بندی‌های ویدیو'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name_fa


class SiteVideo(models.Model):
    SOURCE_CHOICES = [('upload', 'آپلود مستقیم'), ('embed', 'ویدیو خارجی (iframe)')]
    PLATFORM_CHOICES = [
        ('', '—'),
        ('youtube', 'یوتیوب'),
        ('aparat', 'آپارات'),
        ('vimeo', 'ویمئو'),
        ('other', 'سایر'),
    ]

    category = models.ForeignKey(
        VideoCategory, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='videos', verbose_name='دسته‌بندی'
    )
    title_fa = models.CharField(max_length=255, verbose_name='عنوان فارسی')
    title_en = models.CharField(max_length=255, blank=True, verbose_name='English Title')
    title_ar = models.CharField(max_length=255, blank=True, verbose_name='العنوان العربي')
    description_fa = models.TextField(blank=True, verbose_name='توضیح فارسی')
    description_en = models.TextField(blank=True, verbose_name='English Description')
    description_ar = models.TextField(blank=True, verbose_name='الوصف العربي')
    source_type = models.CharField(
        max_length=10, choices=SOURCE_CHOICES, default='embed', verbose_name='نوع منبع'
    )
    file_path = models.FileField(
        upload_to='videos/', blank=True, null=True, verbose_name='فایل ویدیو',
        validators=[validate_video_size(50)],
        help_text='حداکثر ۵۰ MB — توصیه: ویدیو را در آپارات آپلود کنید و از کد embed استفاده نمایید'
    )
    platform = models.CharField(
        max_length=10, choices=PLATFORM_CHOICES, blank=True, default='', verbose_name='پلتفرم'
    )
    embed_code = models.TextField(
        blank=True,
        verbose_name='کد iframe',
        help_text='کد &lt;iframe&gt; را از صفحه ویدیو کپی کنید: یوتیوب ← اشتراک‌گذاری ← جاسازی | آپارات ← اشتراک‌گذاری ← کد تعبیه (گزینه iframe)'
    )
    thumbnail = ProcessedImageField(
        upload_to='videos/thumbnails/', blank=True, null=True, verbose_name='تصویر بند انگشتی',
        processors=[ResizeToFit(640, 360)],
        format='WEBP', options={'quality': 80},
        validators=[validate_image_size(5)],
        help_text='حداکثر ۵ MB — به‌صورت خودکار به ۶۴۰×۳۶۰ و WebP تبدیل می‌شود'
    )
    duration_sec = models.PositiveIntegerField(null=True, blank=True, verbose_name='مدت زمان (ثانیه)')
    views_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    is_published = models.BooleanField(default=False, verbose_name='منتشر شده')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انتشار')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ویدیو'
        verbose_name_plural = 'ویدیوها'
        ordering = ['-published_at', 'sort_order']

    def __str__(self):
        return self.title_fa

    def duration_display(self):
        """مدت زمان به فرمت MM:SS یا HH:MM:SS"""
        if not self.duration_sec:
            return ''
        m, s = divmod(self.duration_sec, 60)
        h, m = divmod(m, 60)
        if h:
            return f'{h:02d}:{m:02d}:{s:02d}'
        return f'{m:02d}:{s:02d}'
