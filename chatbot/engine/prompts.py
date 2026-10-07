from .safety import SAFETY_POLICY

DEFAULT_PROMPTS = {
    'fa': (
        'تو {name} هستی. مؤدب، کوتاه و روشن پاسخ بده. '
        'زبان پاسخ فارسی است مگر اینکه کاربر به زبان دیگری بنویسد. '
        'اگر سؤال خارج از چشم‌پزشکی یا این مطب بود، مؤدبانه محدوده کمکت را بگو '
        'و به تماس با مطب راهنمایی کن.'
    ),
    'en': (
        'You are {name}. Be polite, concise, and clear. '
        'Reply in English unless the user writes in another language. '
        'If the question is outside ophthalmology or this clinic, '
        'politely say so and suggest contacting the office.'
    ),
    'ar': (
        'أنت {name}. أجب بأدب واختصار ووضوح. '
        'أجب بالعربية إلا إذا كتب المستخدم بلغة أخرى. '
        'إذا كان السؤال خارج طب العيون أو هذه العيادة، '
        'وضّح ذلك بلطف واقترح التواصل مع العيادة.'
    ),
}

KNOWLEDGE_INSTRUCTIONS = {
    'hybrid': (
        'اگر بخش «دانش مطب» مرتبط بود، همان را مبنا قرار بده. '
        'اگر نبود، از دانش عمومی چشم‌پزشکی با احتیاط استفاده کن و بگو جایگزین معاینه نیست.'
    ),
    'rag_only': (
        'فقط از بخش «دانش مطب» پاسخ بده. اگر پاسخ در آن نبود بگو این مورد در اطلاعات مطب ثبت نشده '
        'و پیشنهاد تماس با مطب بده. از دانش عمومی مدل استفاده نکن.'
    ),
    'llm_only': (
        'از دانش خودت استفاده کن. فایل جداگانه‌ای در اختیار نداری. '
        'باز هم هیچ دارویی تجویز نکن.'
    ),
}


def build_system_prompt(profile, language):
    lang = language if language in DEFAULT_PROMPTS else 'fa'
    name = {
        'fa': profile.assistant_name_fa,
        'en': profile.assistant_name_en,
        'ar': profile.assistant_name_ar,
    }.get(lang) or profile.assistant_name_fa

    custom = {
        'fa': profile.prompt_fa,
        'en': profile.prompt_en,
        'ar': profile.prompt_ar,
    }.get(lang) or ''
    custom = (custom or '').strip() or DEFAULT_PROMPTS[lang].format(name=name)
    if '{name}' in custom:
        custom = custom.format(name=name)

    mode = profile.knowledge_mode or 'hybrid'
    mode_text = KNOWLEDGE_INSTRUCTIONS.get(mode, KNOWLEDGE_INSTRUCTIONS['hybrid'])

    return (
        f'{custom}\n\n'
        f'نام دستیار: {name}\n'
        f'حالت دانش: {mode_text}\n\n'
        f'{SAFETY_POLICY}'
    )
