from django.db import models


class KnowledgeChunk(models.Model):
    """یک تکهٔ دانش به‌همراه بردارش. جستجو داخل PostgreSQL است، بدون Chroma."""

    profile = models.ForeignKey(
        'chatbot.ChatbotProfile',
        on_delete=models.CASCADE,
        related_name='chunks',
        verbose_name='پروفایل',
    )
    source_type = models.CharField(max_length=32, verbose_name='نوع منبع')
    source_key = models.CharField(max_length=80, verbose_name='کلید منبع')
    source_label = models.CharField(max_length=255, blank=True, verbose_name='نام منبع')
    text = models.TextField(verbose_name='متن')
    embedding = models.JSONField(default=list, verbose_name='بردار')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'قطعهٔ دانش'
        verbose_name_plural = 'قطعه‌های دانش RAG'
        indexes = [
            models.Index(fields=['profile', 'source_type']),
            models.Index(fields=['profile', 'source_key']),
        ]

    def __str__(self):
        return f'{self.source_label or self.source_key}'
