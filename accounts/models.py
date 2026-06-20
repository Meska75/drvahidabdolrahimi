import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('superadmin', 'مدیر ارشد'),
        ('editor', 'ویرایشگر'),
        ('author', 'نویسنده'),
        ('viewer', 'بازدیدکننده'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='کاربر'
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='viewer', verbose_name='نقش'
    )
    phone = models.CharField(
        max_length=20, blank=True, unique=True, null=True,
        verbose_name='شماره موبایل',
        help_text='برای ورود با شماره موبایل — مثال: 09013434195'
    )
    bio_fa = models.TextField(blank=True, verbose_name='بیوگرافی فارسی')
    bio_en = models.TextField(blank=True, verbose_name='English Bio')
    bio_ar = models.TextField(blank=True, verbose_name='السيرة الذاتية')
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, verbose_name='تصویر پروفایل'
    )

    class Meta:
        verbose_name = 'پروفایل کاربری'
        verbose_name_plural = 'پروفایل‌های کاربری'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='email_token', verbose_name='کاربر'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'توکن تأیید ایمیل'
        verbose_name_plural = 'توکن‌های تأیید ایمیل'

    def is_expired(self):
        # لینک تأیید ۴۸ ساعت اعتبار دارد
        return (timezone.now() - self.created_at).total_seconds() > 48 * 3600

    def __str__(self):
        return f'توکن برای {self.user.username}'
