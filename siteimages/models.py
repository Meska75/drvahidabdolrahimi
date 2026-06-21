from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from utils.image_validators import validate_image_size
from main.models import SiteBanner


# ── Proxy برای SiteBanner — نمایش زیر بخش «مدیریت تصاویر سایت» ──
class SiteBannerProxy(SiteBanner):
    class Meta:
        proxy = True
        app_label = 'siteimages'
        verbose_name = 'بنر سایت'
        verbose_name_plural = 'بنرهای سایت'


class DoctorPhoto(models.Model):
    TYPE_CHOICES = [
        ('profile',   'تصویر پروفایل — صفحه درباره ما (بالا)'),
        ('biography', 'تصویر بیوگرافی — صفحه درباره ما (پایین)'),
        ('surgery',   'تصویر جراحی — صفحه خدمات جراحی'),
    ]

    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, unique=True, verbose_name='نوع'
    )
    image = ProcessedImageField(
        upload_to='doctor_photos/', verbose_name='تصویر',
        processors=[ResizeToFit(900, 900)],
        format='WEBP', options={'quality': 85},
        validators=[validate_image_size(8)],
        help_text='حداکثر ۸ MB — فرمت WebP — حداکثر ۹۰۰×۹۰۰'
    )
    alt_fa = models.CharField(max_length=200, blank=True, verbose_name='Alt فارسی')
    alt_en = models.CharField(max_length=200, blank=True, verbose_name='Alt EN')
    alt_ar = models.CharField(max_length=200, blank=True, verbose_name='Alt عربي')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'siteimages'
        verbose_name = 'عکس دکتر'
        verbose_name_plural = 'عکس‌های دکتر'

    def __str__(self):
        return self.get_type_display()


class BuildingPhoto(models.Model):
    image = ProcessedImageField(
        upload_to='building/', verbose_name='تصویر',
        processors=[ResizeToFit(1200, 900)],
        format='WEBP', options={'quality': 85},
        validators=[validate_image_size(8)],
        help_text='حداکثر ۸ MB — نمای بیرونی ساختمان'
    )
    caption_fa = models.CharField(max_length=200, blank=True, verbose_name='توضیح فارسی')
    caption_en = models.CharField(max_length=200, blank=True, verbose_name='English Caption')
    caption_ar = models.CharField(max_length=200, blank=True, verbose_name='التسمية العربية')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        app_label = 'siteimages'
        verbose_name = 'عکس ساختمان / نمای بیرونی'
        verbose_name_plural = 'عکس‌های ساختمان / نمای بیرونی'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.caption_fa or f'عکس ساختمان {self.pk}'


class ClinicInteriorPhoto(models.Model):
    """تصاویر داخل مطب — نمایش در بخش گالری صفحه اصلی"""

    image = ProcessedImageField(
        upload_to='clinic_interior/', verbose_name='تصویر',
        processors=[ResizeToFit(800, 800)],
        format='WEBP', options={'quality': 85},
        validators=[validate_image_size(8)],
        help_text='حداکثر ۸ MB — تصاویر داخل مطب برای نمایش در صفحه اصلی'
    )
    caption_fa = models.CharField(max_length=200, blank=True, verbose_name='توضیح فارسی')
    caption_en = models.CharField(max_length=200, blank=True, verbose_name='English Caption')
    caption_ar = models.CharField(max_length=200, blank=True, verbose_name='التسمية العربية')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        app_label = 'siteimages'
        verbose_name = 'عکس داخل مطب'
        verbose_name_plural = 'عکس‌های داخل مطب (صفحه اصلی)'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.caption_fa or f'عکس مطب {self.pk}'
