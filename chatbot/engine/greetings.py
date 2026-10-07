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
