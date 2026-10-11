"""سلام اول بدون فراخوانی مدل — به زبان صفحه سایت."""

DEFAULT_GREETINGS = {
    'fa': (
        'سلام، من {name} هستم. می‌توانم درباره مطب، خدمات چشم‌پزشکی '
        'و نحوه مراجعه راهنمایی‌تان کنم. چگونه می‌توانم کمکتان کنم؟'
    ),
    'en': (
        'Hello, I am {name}. I can help with clinic information, '
        'ophthalmology services, and how to visit. How can I help you?'
    ),
    'ar': (
        'مرحباً، أنا {name}. يمكنني مساعدتك بمعلومات العيادة وخدمات '
        'طب العيون وكيفية المراجعة. كيف يمكنني مساعدتك؟'
    ),
}


def greeting_text(language, assistant_name):
    lang = language if language in DEFAULT_GREETINGS else 'fa'
    template = DEFAULT_GREETINGS[lang]
    return template.format(name=assistant_name or 'دستیار')


def ensure_stored_greeting(conversation, text):
    """اگر کاربر هنوز پیامی نفرستاده، سلام ذخیره‌شده را با زبان همین صفحه یکی کن."""
    from chatbot.models import ChatMessage

    if conversation.messages.filter(role='user').exists():
        return
    first = conversation.messages.order_by('created_at', 'id').first()
    if first is None:
        ChatMessage.objects.create(
            conversation=conversation, role='assistant', content=text,
        )
        return
    if first.role == 'assistant' and first.content != text:
        first.content = text
        first.save(update_fields=['content'])
