from django.db import models


class Conversation(models.Model):
    profile = models.ForeignKey(
        'chatbot.ChatbotProfile',
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name='پروفایل',
    )
    session_key = models.CharField(
        max_length=64,
        verbose_name='شناسه مهمان',
        help_text='کوکی مرورگر بدون اکانت — حداکثر ۷ روز از آخرین پیام',
    )
    language = models.CharField(max_length=8, default='fa', verbose_name='زبان')
    source = models.CharField(
        max_length=16, default='widget',
        verbose_name='منبع',
        help_text='widget = همین سایت، link = سایت دیگر',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'گفتگو'
        verbose_name_plural = '۵. گفتگوها'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.profile} / {self.language} / {self.created_at:%Y-%m-%d %H:%M}'


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'کاربر'),
        ('assistant', 'دستیار'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='گفتگو',
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, verbose_name='نقش')
    content = models.TextField(verbose_name='متن')
    used_fallback = models.BooleanField(
        default=False, verbose_name='پاسخ جایگزین (مدل در دسترس نبود)',
    )
    internal_error = models.TextField(
        blank=True, verbose_name='خطای فنی (فقط ادمین)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌های گفتگو'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:40]}'


class RateLimitHit(models.Model):
    """شمارش پیام برای محدودیت نرخ — روی دیتابیس تا بین چند worker درست کار کند."""

    key = models.CharField(max_length=160, db_index=True)
    window_type = models.CharField(max_length=8)  # minute | hour
    window_start = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'شمارنده محدودیت'
        verbose_name_plural = 'شمارنده‌های محدودیت'
        unique_together = ('key', 'window_type', 'window_start')
