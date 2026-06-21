from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from utils.image_validators import validate_image_size


class Category(models.Model):
    name_fa = models.CharField(max_length=100, verbose_name='عنوان فارسی')
    name_en = models.CharField(max_length=100, verbose_name='English Title')
    name_ar = models.CharField(max_length=100, verbose_name='العنوان العربي')
    slug = models.SlugField(unique=True, allow_unicode=True)
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name_fa


class Post(models.Model):
    title_fa = models.CharField(max_length=255, verbose_name='عنوان فارسی')
    title_en = models.CharField(max_length=255, verbose_name='English Title')
    title_ar = models.CharField(max_length=255, verbose_name='العنوان العربي')
    slug = models.SlugField(unique=True, allow_unicode=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='posts', verbose_name='دسته‌بندی'
    )

    summary_fa = models.TextField(blank=True, verbose_name='خلاصه فارسی')
    summary_en = models.TextField(blank=True, verbose_name='English Summary')
    summary_ar = models.TextField(blank=True, verbose_name='الملخص العربي')

    content_fa = RichTextUploadingField(verbose_name='محتوا فارسی', config_name='rtl')
    content_en = RichTextUploadingField(verbose_name='English Content', config_name='ltr')
    content_ar = RichTextUploadingField(verbose_name='المحتوى العربي', config_name='rtl')

    image = ProcessedImageField(
        upload_to='blog/', blank=True, null=True, verbose_name='تصویر شاخص',
        processors=[ResizeToFit(1200, 800)],
        format='WEBP', options={'quality': 82},
        validators=[validate_image_size(8)],
        help_text='حداکثر ۸ MB — به‌صورت خودکار به حداکثر ۱۲۰۰×۸۰۰ و WebP تبدیل می‌شود'
    )
    author = models.CharField(
        max_length=100, default='دکتر وحید عبدالرحیمی', verbose_name='نویسنده'
    )

    meta_title_fa = models.CharField(max_length=70, blank=True, verbose_name='عنوان SEO فارسی')
    meta_title_en = models.CharField(max_length=70, blank=True, verbose_name='SEO Title EN')
    meta_title_ar = models.CharField(max_length=70, blank=True, verbose_name='عنوان SEO عربي')
    meta_description_fa = models.CharField(max_length=165, blank=True, verbose_name='توضیح SEO فارسی')
    meta_description_en = models.CharField(max_length=165, blank=True, verbose_name='SEO Description EN')
    meta_description_ar = models.CharField(max_length=165, blank=True, verbose_name='وصف SEO عربي')

    published_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ انتشار')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    is_published = models.BooleanField(default=False, verbose_name='منتشر شده')
    views_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at']

    def __str__(self):
        return self.title_fa


class Comment(models.Model):
    LANG_CHOICES = [('fa', 'فارسی'), ('en', 'English'), ('ar', 'العربية')]

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments', verbose_name='مقاله'
    )
    name = models.CharField(max_length=100, verbose_name='نام')
    email = models.EmailField(blank=True, verbose_name='ایمیل')
    body = models.TextField(verbose_name='متن نظر')
    language = models.CharField(
        max_length=2, choices=LANG_CHOICES, default='fa', verbose_name='زبان'
    )
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.name} — {self.post.title_fa[:40]}'
