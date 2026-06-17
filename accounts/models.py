from django.db import models
from django.contrib.auth.models import User


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
