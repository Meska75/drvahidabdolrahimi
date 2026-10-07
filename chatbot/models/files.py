import os
from django.core.exceptions import ValidationError
from django.db import models


ALLOWED_RAG_EXTENSIONS = {'.pdf', '.txt', '.md'}
MAX_RAG_FILE_BYTES = 10 * 1024 * 1024


def validate_rag_file(uploaded):
    name = getattr(uploaded, 'name', '') or ''
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_RAG_EXTENSIONS:
        raise ValidationError('فقط فایل PDF، TXT یا Markdown مجاز است.')
    size = getattr(uploaded, 'size', 0) or 0
    if size > MAX_RAG_FILE_BYTES:
        raise ValidationError('حجم فایل نباید بیشتر از ۱۰ مگابایت باشد.')


def knowledge_upload_to(instance, filename):
    safe = os.path.basename(filename)
    return f'chatbot/knowledge/{instance.profile_id}/{safe}'


class KnowledgeFile(models.Model):
    """کتابخانه فایل.

    in_rag=True یعنی الان در جستجوی RAG است.
    می‌توان از RAG برداشت ولی فایل را نگه داشت و بعداً دوباره اضافه کرد.
    """

    STATUS_CHOICES = [
        ('ready', 'آماده‌ی استفاده'),
        ('indexing', 'در حال ایندکس'),
        ('error', 'خطا در ایندکس'),
        ('idle', 'فقط در کتابخانه (خارج از RAG)'),
    ]

    profile = models.ForeignKey(
        'chatbot.ChatbotProfile',
        on_delete=models.CASCADE,
        related_name='knowledge_files',
        verbose_name='پروفایل',
    )
    file = models.FileField(
        upload_to=knowledge_upload_to,
        verbose_name='فایل',
        validators=[validate_rag_file],
    )
    original_name = models.CharField(max_length=255, verbose_name='نام فایل')
    in_rag = models.BooleanField(
        default=False,
        verbose_name='داخل RAG است',
        help_text='اگر بردارید، فایل در کتابخانه می‌ماند و می‌توان دوباره اضافه کرد.',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='idle',
        verbose_name='وضعیت ایندکس',
    )
    chunk_count = models.PositiveIntegerField(default=0, verbose_name='تعداد قطعات')
    last_error = models.TextField(blank=True, verbose_name='خطای ایندکس (ادمین)')
    indexed_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان ایندکس')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'فایل دانش'
        verbose_name_plural = '۴. فایل‌های RAG'
        ordering = ['-uploaded_at']

    def __str__(self):
        mark = 'در RAG' if self.in_rag else 'کتابخانه'
        return f'{self.original_name} ({mark})'

    def save(self, *args, **kwargs):
        if self.file and not self.original_name:
            self.original_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)
