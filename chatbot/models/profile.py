from django.db import models


class ChatbotProfile(models.Model):
    """یک پروفایل = یک پزشک / یک سایت.

    سایت همین پروژه از پروفایل پیش‌فرض استفاده می‌کند.
    سایت دیگر دکتر با کلید نسخهٔ لینک به همان موتور وصل می‌شود
    ولی پرامپت، مدل و RAG جدا دارد.
    """

    KNOWLEDGE_CHOICES = [
        ('hybrid', 'ترکیبی: فایل‌های RAG + دانش مدل (پیشنهادی)'),
        ('rag_only', 'فقط فایل‌های RAG (اگر در فایل نبود، نمی‌دانم)'),
        ('llm_only', 'فقط دانش مدل — بدون جستجوی فایل'),
    ]

    slug = models.SlugField(
        unique=True,
        verbose_name='شناسه انگلیسی',
        help_text='مثال: abdolrahimi — در آدرس و کالکشن RAG استفاده می‌شود',
    )
    title = models.CharField(max_length=120, verbose_name='عنوان نمایشی')
    is_default = models.BooleanField(
        default=False,
        verbose_name='پروفایل همین سایت',
        help_text='فقط یکی باید تیک داشته باشد. ویجت صفحات فارسی/انگلیسی/عربی از این پروفایل می‌آید.',
    )

    widget_enabled = models.BooleanField(
        default=False,
        verbose_name='نمایش آیکون روی سایت',
        help_text='خاموش = آیکون مخفی. روشن = آیکون گوشه صفحه.',
    )
    link_enabled = models.BooleanField(
        default=False,
        verbose_name='فعال بودن نسخه لینک (FastAPI)',
    )
    link_api_key_encrypted = models.TextField(
        blank=True,
        verbose_name='کلید نسخه لینک (رمزشده)',
        help_text='کلید را در فرم پایین وارد کنید؛ در دیتابیس رمز می‌شود.',
    )
    allowed_origins = models.TextField(
        blank=True,
        verbose_name='دامنه‌های مجاز نسخه لینک',
        help_text='هر خط یک آدرس، مثال: https://other-doctor.ir',
    )

    knowledge_mode = models.CharField(
        max_length=20,
        choices=KNOWLEDGE_CHOICES,
        default='hybrid',
        verbose_name='منبع پاسخ',
    )

    prompt_fa = models.TextField(blank=True, verbose_name='پرامپت فارسی')
    prompt_en = models.TextField(blank=True, verbose_name='پرامپت انگلیسی')
    prompt_ar = models.TextField(blank=True, verbose_name='پرامپت عربی')

    assistant_name_fa = models.CharField(
        max_length=120, default='دستیار هوش مصنوعی دکتر عبدالرحیمی',
        verbose_name='نام دستیار (فارسی)',
    )
    assistant_name_en = models.CharField(
        max_length=120, default='Dr. Abdolrahimi AI assistant',
        verbose_name='نام دستیار (انگلیسی)',
    )
    assistant_name_ar = models.CharField(
        max_length=120, default='مساعد الدكتور عبدالرحيمي الذكي',
        verbose_name='نام دستیار (عربی)',
    )

    rate_limit_per_minute = models.PositiveSmallIntegerField(
        default=10, verbose_name='حداکثر پیام در دقیقه',
    )
    rate_limit_per_hour = models.PositiveSmallIntegerField(
        default=40, verbose_name='حداکثر پیام در ساعت',
    )

    active_llm = models.ForeignKey(
        'chatbot.LlmConnection',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='active_for_profiles',
        verbose_name='اتصال فعال مدل چت',
    )
    active_embedding = models.ForeignKey(
        'chatbot.EmbeddingConnection',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='active_for_profiles',
        verbose_name='اتصال فعال مدل RAG',
    )

    sync_site_faq = models.BooleanField(default=False, verbose_name='سوالات متداول')
    sync_site_services = models.BooleanField(default=False, verbose_name='خدمات مطب و جراحی')
    sync_site_doctor = models.BooleanField(default=False, verbose_name='تحصیلات و افتخارات پزشک')
    sync_site_clinic = models.BooleanField(default=False, verbose_name='مطب، آدرس و ساعت کار')
    sync_site_team = models.BooleanField(default=False, verbose_name='اعضای تیم')
    sync_site_blog = models.BooleanField(default=False, verbose_name='مقالات منتشرشدهٔ بلاگ')
    sync_site_auto = models.BooleanField(
        default=False,
        verbose_name='به‌روزرسانی خودکار با ذخیره در سایت',
        help_text='اگر روشن باشد، ذخیره یا حذف همان بخش‌ها RAG این پروفایل را هم عوض می‌کند. ویجت و نسخه لینک هر دو از همین ایندکس می‌خوانند.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پروفایل چت‌بات'
        verbose_name_plural = '۱. پروفایل‌ها و پرامپت'
        ordering = ['-is_default', 'title']

    def __str__(self):
        return self.title

    def origin_list(self):
        return [
            line.strip().rstrip('/')
            for line in (self.allowed_origins or '').splitlines()
            if line.strip()
        ]

    @classmethod
    def default(cls):
        return cls.objects.filter(is_default=True).first()
