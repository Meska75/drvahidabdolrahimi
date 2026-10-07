from django.db import migrations


DEFAULT_PROMPT_FA = (
    'تو {name} هستی. مؤدب، کوتاه و روشن پاسخ بده. '
    'زبان پاسخ فارسی است مگر اینکه کاربر به زبان دیگری بنویسد. '
    'اگر سؤال خارج از چشم‌پزشکی یا این مطب بود، مؤدبانه محدوده کمکت را بگو '
    'و به تماس با مطب راهنمایی کن.'
)
DEFAULT_PROMPT_EN = (
    'You are {name}. Be polite, concise, and clear. '
    'Reply in English unless the user writes in another language. '
    'If the question is outside ophthalmology or this clinic, '
    'politely say so and suggest contacting the office.'
)
DEFAULT_PROMPT_AR = (
    'أنت {name}. أجب بأدب واختصار ووضوح. '
    'أجب بالعربية إلا إذا كتب المستخدم بلغة أخرى. '
    'إذا كان السؤال خارج طب العيون أو هذه العيادة، '
    'وضّح ذلك بلطف واقترح التواصل مع العيادة.'
)


def create_default_profile(apps, schema_editor):
    ChatbotProfile = apps.get_model('chatbot', 'ChatbotProfile')
    if ChatbotProfile.objects.filter(slug='abdolrahimi').exists():
        return
    ChatbotProfile.objects.create(
        slug='abdolrahimi',
        title='مطب دکتر عبدالرحیمی',
        is_default=True,
        widget_enabled=False,
        link_enabled=False,
        knowledge_mode='hybrid',
        prompt_fa=DEFAULT_PROMPT_FA,
        prompt_en=DEFAULT_PROMPT_EN,
        prompt_ar=DEFAULT_PROMPT_AR,
        assistant_name_fa='دستیار هوش مصنوعی دکتر عبدالرحیمی',
        assistant_name_en='Dr. Abdolrahimi AI assistant',
        assistant_name_ar='مساعد الدكتور عبدالرحيمي الذكي',
        rate_limit_per_minute=10,
        rate_limit_per_hour=40,
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_profile, noop),
    ]
