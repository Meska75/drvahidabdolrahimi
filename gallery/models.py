from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from utils.image_validators import validate_image_size


class GalleryTag(models.Model):
    name_fa = models.CharField(max_length=80, verbose_name='نام فارسی')
    name_en = models.CharField(max_length=80, blank=True, verbose_name='English Name')
    name_ar = models.CharField(max_length=80, blank=True, verbose_name='الاسم العربي')
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name='اسلاگ')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'تگ گالری'
        verbose_name_plural = 'تگ‌های گالری'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name_fa


class GalleryImage(models.Model):
    title_fa = models.CharField(max_length=200, blank=True, verbose_name='عنوان فارسی')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='English Title')
    title_ar = models.CharField(max_length=200, blank=True, verbose_name='العنوان العربي')
    description_fa = models.CharField(max_length=300, blank=True, verbose_name='توضیح فارسی')
    description_en = models.CharField(max_length=300, blank=True, verbose_name='English Description')
    description_ar = models.CharField(max_length=300, blank=True, verbose_name='الوصف العربي')
    image = ProcessedImageField(
        upload_to='gallery/', verbose_name='تصویر',
        processors=[ResizeToFit(1600, 1200)],
        format='WEBP', options={'quality': 85},
        validators=[validate_image_size(10)],
        help_text='حداکثر ۱۰ MB — به‌صورت خودکار به حداکثر ۱۶۰۰×۱۲۰۰ و WebP تبدیل می‌شود'
    )
    alt_fa = models.CharField(max_length=200, blank=True, verbose_name='Alt فارسی')
    alt_en = models.CharField(max_length=200, blank=True, verbose_name='Alt EN')
    alt_ar = models.CharField(max_length=200, blank=True, verbose_name='Alt عربي')
    tags = models.ManyToManyField(
        GalleryTag, blank=True, related_name='images', verbose_name='تگ‌ها'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'تصویر گالری'
        verbose_name_plural = 'تصاویر گالری'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title_fa or f'تصویر {self.id}'

    def tag_classes(self):
        """برای Isotope.js — مثلاً: tag-clinic tag-surgery"""
        return ' '.join([f'tag-{t.slug}' for t in self.tags.all()])
