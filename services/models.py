from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from utils.image_validators import validate_image_size


class ServiceItem(models.Model):
    TYPE_CHOICES = [('office', 'خدمات مطب'), ('surgery', 'خدمات جراحی')]

    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='office', verbose_name='نوع خدمت'
    )
    title_fa = models.CharField(max_length=200, verbose_name='عنوان فارسی')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='English Title')
    title_ar = models.CharField(max_length=200, blank=True, verbose_name='العنوان العربي')

    # متن خلاصه — نمایش در کارت‌های صفحه اصلی (کاروسل)
    summary_fa = models.CharField(
        max_length=90, blank=True, verbose_name='متن خلاصه — فارسی',
        help_text='حداکثر ۹۰ کاراکتر — نمایش در کارت‌های صفحه اصلی'
    )
    summary_en = models.CharField(
        max_length=90, blank=True, verbose_name='Summary — English',
        help_text='Max 90 characters — shown on home page cards'
    )
    summary_ar = models.CharField(
        max_length=90, blank=True, verbose_name='الملخص — عربي',
        help_text='الحد الأقصى ٩٠ حرفًا — يظهر في بطاقات الصفحة الرئيسية'
    )

    # توضیح کوتاه کامل — نمایش در کارت‌های صفحه خدمات
    description_fa = models.CharField(
        max_length=250, blank=True, verbose_name='توضیح کوتاه — فارسی',
        help_text='حداکثر ۲۵۰ کاراکتر — نمایش در صفحه خدمات'
    )
    description_en = models.CharField(
        max_length=250, blank=True, verbose_name='Description — English',
        help_text='Max 250 characters — shown on services page'
    )
    description_ar = models.CharField(
        max_length=250, blank=True, verbose_name='الوصف — عربي',
        help_text='الحد الأقصى ٢٥٠ حرفًا — يظهر في صفحة الخدمات'
    )

    image = ProcessedImageField(
        upload_to='services/', blank=True, null=True, verbose_name='تصویر',
        processors=[ResizeToFit(800, 600)],
        format='WEBP', options={'quality': 82},
        validators=[validate_image_size(8)],
        help_text='حداکثر ۸ MB — به‌صورت خودکار فشرده و به WebP تبدیل می‌شود'
    )
    meta_title_fa = models.CharField(max_length=70, blank=True, verbose_name='عنوان SEO فارسی')
    meta_title_en = models.CharField(max_length=70, blank=True, verbose_name='SEO Title EN')
    meta_title_ar = models.CharField(max_length=70, blank=True, verbose_name='عنوان SEO عربي')
    meta_description_fa = models.CharField(max_length=165, blank=True, verbose_name='توضیح SEO فارسی')
    meta_description_en = models.CharField(max_length=165, blank=True, verbose_name='SEO Description EN')
    meta_description_ar = models.CharField(max_length=165, blank=True, verbose_name='وصف SEO عربي')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'خدمت'
        verbose_name_plural = 'خدمات'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title_fa
