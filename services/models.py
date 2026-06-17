from django.db import models


class ServiceCategory(models.Model):
    TYPE_CHOICES = [('office', 'خدمات مطب'), ('surgery', 'جراحی')]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='نوع')
    name_fa = models.CharField(max_length=150, verbose_name='نام فارسی')
    name_en = models.CharField(max_length=150, blank=True, verbose_name='English Name')
    name_ar = models.CharField(max_length=150, blank=True, verbose_name='الاسم العربي')
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name='اسلاگ')

    class Meta:
        verbose_name = 'دسته‌بندی خدمات'
        verbose_name_plural = 'دسته‌بندی‌های خدمات'

    def __str__(self):
        return self.name_fa


class ServiceItem(models.Model):
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE,
        related_name='items', verbose_name='دسته‌بندی'
    )
    title_fa = models.CharField(max_length=200, verbose_name='عنوان فارسی')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='English Title')
    title_ar = models.CharField(max_length=200, blank=True, verbose_name='العنوان العربي')
    description_fa = models.TextField(blank=True, verbose_name='توضیح فارسی')
    description_en = models.TextField(blank=True, verbose_name='English Description')
    description_ar = models.TextField(blank=True, verbose_name='الوصف العربي')
    icon_class = models.CharField(max_length=60, blank=True, verbose_name='آیکون CSS')
    image = models.ImageField(
        upload_to='services/', blank=True, null=True, verbose_name='تصویر'
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
