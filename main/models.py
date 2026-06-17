from django.db import models
from django.contrib.auth.models import User


class ContactMessage(models.Model):
    LANG_CHOICES = [('fa', 'فارسی'), ('en', 'English'), ('ar', 'العربية')]

    full_name = models.CharField(max_length=120, verbose_name='نام کامل')
    phone = models.CharField(max_length=20, blank=True, verbose_name='تلفن')
    email = models.EmailField(blank=True, verbose_name='ایمیل')
    subject = models.CharField(max_length=200, blank=True, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    language = models.CharField(
        max_length=2, choices=LANG_CHOICES, default='fa', verbose_name='زبان'
    )
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    is_replied = models.BooleanField(default=False, verbose_name='پاسخ داده شده')
    replied_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='replies', verbose_name='پاسخ‌دهنده'
    )
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پاسخ')
    admin_note = models.TextField(blank=True, verbose_name='یادداشت ادمین')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} — {self.subject or "بدون موضوع"}'


class SiteSetting(models.Model):
    TYPE_CHOICES = [
        ('text', 'متن کوتاه'),
        ('textarea', 'متن بلند'),
        ('image', 'تصویر'),
        ('boolean', 'بله/خیر'),
        ('number', 'عدد'),
        ('url', 'لینک'),
    ]

    key = models.CharField(max_length=100, unique=True, verbose_name='کلید')
    group_name = models.CharField(max_length=60, verbose_name='گروه')
    label_fa = models.CharField(max_length=150, verbose_name='برچسب فارسی')
    value_fa = models.TextField(blank=True, verbose_name='مقدار فارسی')
    value_en = models.TextField(blank=True, verbose_name='مقدار انگلیسی')
    value_ar = models.TextField(blank=True, verbose_name='مقدار عربی')
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='text', verbose_name='نوع'
    )
    is_editable = models.BooleanField(default=True, verbose_name='قابل ویرایش')

    class Meta:
        verbose_name = 'تنظیم سایت'
        verbose_name_plural = 'تنظیمات سایت'
        ordering = ['group_name', 'key']

    def __str__(self):
        return f'{self.group_name} / {self.key}'


class SiteBanner(models.Model):
    LOCATION_CHOICES = [
        ('home_hero', 'اسلایدر صفحه اصلی'),
        ('page_hero', 'هدر صفحات داخلی'),
    ]

    location = models.CharField(
        max_length=20, choices=LOCATION_CHOICES, default='home_hero', verbose_name='موقعیت'
    )
    image = models.ImageField(
        upload_to='banners/', verbose_name='تصویر',
        help_text='اسلایدر صفحه اصلی: ۱۹۲۰×۸۰۰ پیکسل — هدر صفحات داخلی: ۱۹۲۰×۵۰۰ پیکسل — فرمت: JPG یا WebP — حداکثر حجم: ۱ مگابایت'
    )
    caption_fa = models.CharField(max_length=255, blank=True, verbose_name='کپشن فارسی')
    caption_en = models.CharField(max_length=255, blank=True, verbose_name='English Caption')
    caption_ar = models.CharField(max_length=255, blank=True, verbose_name='التسمية التوضيحية')
    alt_fa = models.CharField(max_length=200, blank=True, verbose_name='Alt فارسی')
    alt_en = models.CharField(max_length=200, blank=True, verbose_name='Alt EN')
    alt_ar = models.CharField(max_length=200, blank=True, verbose_name='Alt عربي')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'بنر سایت'
        verbose_name_plural = 'بنرهای سایت'
        ordering = ['location', 'sort_order']

    def __str__(self):
        return f'{self.get_location_display()} — {self.sort_order}'


class DoctorEducation(models.Model):
    degree_fa = models.CharField(max_length=200, verbose_name='مدرک فارسی')
    degree_en = models.CharField(max_length=200, blank=True, verbose_name='English Degree')
    degree_ar = models.CharField(max_length=200, blank=True, verbose_name='الدرجة العلمية')
    institution_fa = models.CharField(max_length=200, verbose_name='مؤسسه فارسی')
    institution_en = models.CharField(max_length=200, blank=True, verbose_name='English Institution')
    institution_ar = models.CharField(max_length=200, blank=True, verbose_name='المؤسسة العربية')
    year = models.CharField(max_length=10, blank=True, verbose_name='سال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'تحصیلات پزشک'
        verbose_name_plural = 'تحصیلات پزشک'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.degree_fa} — {self.institution_fa}'


class DoctorAchievement(models.Model):
    title_fa = models.CharField(max_length=255, verbose_name='عنوان فارسی')
    title_en = models.CharField(max_length=255, blank=True, verbose_name='English Title')
    title_ar = models.CharField(max_length=255, blank=True, verbose_name='العنوان العربي')
    year = models.CharField(max_length=10, blank=True, verbose_name='سال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'افتخار پزشک'
        verbose_name_plural = 'افتخارات پزشک'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title_fa


class DoctorClinic(models.Model):
    name_fa = models.CharField(max_length=200, verbose_name='نام فارسی')
    name_en = models.CharField(max_length=200, blank=True, verbose_name='English Name')
    name_ar = models.CharField(max_length=200, blank=True, verbose_name='الاسم العربي')
    address_fa = models.TextField(blank=True, verbose_name='آدرس فارسی')
    address_en = models.TextField(blank=True, verbose_name='English Address')
    address_ar = models.TextField(blank=True, verbose_name='العنوان العربي')
    city_fa = models.CharField(max_length=100, default='تهران', verbose_name='شهر فارسی')
    city_en = models.CharField(max_length=100, default='Tehran', verbose_name='English City')
    city_ar = models.CharField(max_length=100, default='طهران', verbose_name='المدينة العربية')
    phone_1 = models.CharField(max_length=30, blank=True, verbose_name='تلفن اول')
    phone_2 = models.CharField(max_length=30, blank=True, verbose_name='تلفن دوم')
    schedule_fa = models.TextField(blank=True, verbose_name='ساعت کاری فارسی')
    schedule_en = models.TextField(blank=True, verbose_name='English Schedule')
    schedule_ar = models.TextField(blank=True, verbose_name='جدول المواعيد')
    image = models.ImageField(
        upload_to='clinics/', blank=True, null=True, verbose_name='تصویر',
        help_text='ابعاد توصیه‌شده: ۸۰۰×۶۰۰ پیکسل — فرمت: JPG یا PNG — حداکثر حجم: ۳۰۰ کیلوبایت'
    )
    map_url = models.URLField(blank=True, verbose_name='لینک نقشه')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مطب/کلینیک'
        verbose_name_plural = 'مطب‌ها/کلینیک‌ها'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name_fa


class FaqItem(models.Model):
    question_fa = models.TextField(verbose_name='سوال فارسی')
    question_en = models.TextField(blank=True, verbose_name='English Question')
    question_ar = models.TextField(blank=True, verbose_name='السؤال العربي')
    answer_fa = models.TextField(verbose_name='پاسخ فارسی')
    answer_en = models.TextField(blank=True, verbose_name='English Answer')
    answer_ar = models.TextField(blank=True, verbose_name='الجواب العربي')
    category = models.CharField(max_length=60, default='general', verbose_name='دسته‌بندی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.question_fa[:80]


class PatientTestimonial(models.Model):
    name_fa = models.CharField(max_length=120, verbose_name='نام فارسی')
    name_en = models.CharField(max_length=120, blank=True, verbose_name='English Name')
    name_ar = models.CharField(max_length=120, blank=True, verbose_name='الاسم العربي')
    content_fa = models.TextField(verbose_name='نظر فارسی')
    content_en = models.TextField(blank=True, verbose_name='English Content')
    content_ar = models.TextField(blank=True, verbose_name='المحتوى العربي')
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='امتیاز (۱-۵)'
    )
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_testimonials', verbose_name='تأییدکننده'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ تأیید')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نظر بیمار'
        verbose_name_plural = 'نظرات بیماران'
        ordering = ['-created_at']

    def __str__(self):
        status = 'تأیید شده' if self.is_approved else 'در انتظار'
        return f'{self.name_fa} — {status}'
