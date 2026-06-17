from django.db import models


class TeamMember(models.Model):
    name_fa = models.CharField(max_length=150, verbose_name='نام فارسی')
    name_en = models.CharField(max_length=150, blank=True, verbose_name='English Name')
    name_ar = models.CharField(max_length=150, blank=True, verbose_name='الاسم العربي')
    title_fa = models.CharField(max_length=200, blank=True, verbose_name='سمت فارسی')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='English Title')
    title_ar = models.CharField(max_length=200, blank=True, verbose_name='اللقب العربي')
    bio_fa = models.TextField(blank=True, verbose_name='معرفی فارسی')
    bio_en = models.TextField(blank=True, verbose_name='English Bio')
    bio_ar = models.TextField(blank=True, verbose_name='السيرة الذاتية')
    photo = models.ImageField(
        upload_to='team/', blank=True, null=True, verbose_name='تصویر'
    )
    instagram_url = models.URLField(blank=True, verbose_name='اینستاگرام')
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name='واتساپ')
    telegram_url = models.URLField(blank=True, verbose_name='تلگرام')
    linkedin_url = models.URLField(blank=True, verbose_name='لینکدین')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'عضو تیم'
        verbose_name_plural = 'اعضای تیم'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name_fa
