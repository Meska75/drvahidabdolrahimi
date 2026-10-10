import hashlib

from django.db import models


PROVIDER_CHOICES = [
    ('openai_compatible', 'OpenAI سازگار'),
    ('anthropic', 'Anthropic (Messages API)'),
    ('azure', 'Azure OpenAI'),
]


class LlmConnection(models.Model):
    """اتصال مدل چت. Base URL + کلید + نام مدل کافی است."""

    profile = models.ForeignKey(
        'chatbot.ChatbotProfile',
        on_delete=models.CASCADE,
        related_name='llm_connections',
        verbose_name='پروفایل',
    )
    name = models.CharField(
        max_length=80, verbose_name='نام این اتصال',
        help_text='فقط برای تشخیص در پنل، مثلاً: مدل چت مطب',
    )
    provider = models.CharField(
        max_length=32,
        choices=PROVIDER_CHOICES,
        default='openai_compatible',
        verbose_name='روش اتصال',
    )
    base_url = models.URLField(
        max_length=400, verbose_name='لینک اتصال (Base URL)',
        help_text='آدرس پایهٔ درگاه سازگار با OpenAI، همراه با /v1',
    )
    api_key_encrypted = models.TextField(blank=True, verbose_name='کلید دسترسی (رمزشده)')
    model_name = models.CharField(
        max_length=120, verbose_name='نام مدل',
        help_text='نام مدل روی همان درگاه، مثلاً gpt-4o-mini',
    )
    azure_api_version = models.CharField(
        max_length=40, blank=True, verbose_name='نسخه API آژور',
        help_text='فقط برای Azure، مثلاً 2024-08-01-preview',
    )
    temperature = models.FloatField(default=0.3, verbose_name='Temperature')
    max_tokens = models.PositiveIntegerField(default=800, verbose_name='سقف توکن پاسخ')
    timeout_seconds = models.PositiveSmallIntegerField(default=45, verbose_name='مهلت پاسخ (ثانیه)')
    is_ready = models.BooleanField(
        default=False, verbose_name='آخرین تست اتصال موفق بود',
    )
    last_error = models.TextField(blank=True, verbose_name='آخرین خطای فنی (فقط ادمین)')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'اتصال مدل چت'
        verbose_name_plural = '۲. اتصال‌های مدل چت'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.model_name})'


class EmbeddingConnection(models.Model):
    """اتصال مدل embedding برای RAG — معمولاً همان کلید، با نام مدل دیگر."""

    profile = models.ForeignKey(
        'chatbot.ChatbotProfile',
        on_delete=models.CASCADE,
        related_name='embedding_connections',
        verbose_name='پروفایل',
    )
    name = models.CharField(max_length=80, verbose_name='نام این اتصال')
    provider = models.CharField(
        max_length=32,
        choices=PROVIDER_CHOICES,
        default='openai_compatible',
        verbose_name='روش اتصال',
    )
    base_url = models.URLField(max_length=400, verbose_name='لینک اتصال (Base URL)')
    api_key_encrypted = models.TextField(blank=True, verbose_name='کلید دسترسی (رمزشده)')
    model_name = models.CharField(
        max_length=120, verbose_name='نام مدل embedding',
        help_text='برای فارسی/عربی/انگلیسی: intfloat/multilingual-e5-large',
    )
    azure_api_version = models.CharField(max_length=40, blank=True, verbose_name='نسخه API آژور')
    timeout_seconds = models.PositiveSmallIntegerField(default=60, verbose_name='مهلت پاسخ (ثانیه)')
    is_ready = models.BooleanField(default=False, verbose_name='آخرین تست موفق بود')
    last_error = models.TextField(blank=True, verbose_name='آخرین خطای فنی (فقط ادمین)')
    # اگر مدل embedding عوض شود، بردارهای قبلی نامعتبرند
    fingerprint = models.CharField(
        max_length=64, blank=True, verbose_name='اثر انگشت مدل',
        help_text='با تغییر مدل، ایندکس باید از نو ساخته شود',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'اتصال مدل RAG'
        verbose_name_plural = '۳. اتصال‌های مدل RAG (embedding)'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.model_name})'

    def compute_fingerprint(self):
        """اثر انگشت ۶۴ نویسه‌ای؛ آدرس کامل در این فیلد جا نمی‌شود."""
        raw = f'{self.base_url}|{self.model_name}'.encode('utf-8')
        return hashlib.sha256(raw).hexdigest()
