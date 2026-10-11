import re

DEFAULT_PROMPTS = {
    'fa': (
        'تو {name} هستی. کوتاه و مؤدب جواب بده. '
        'خارج از چشم‌پزشکی یا این مطب، محدوده را بگو و به تماس با مطب راهنمایی کن.'
    ),
    'en': (
        'You are {name}. Be brief and polite. '
        'Outside ophthalmology or this clinic, say so and suggest calling the office.'
    ),
    'ar': (
        'أنت {name}. أجب باختصار وأدب. '
        'خارج طب العيون أو هذه العيادة، وضّح ذلك واقترح الاتصال بالعيادة.'
    ),
}

# قفل زبان روی زبان همین پیام، نه زبان‌های دیگر
LANG_LOCK = {
    'fa': 'فقط فارسی بنویس. واژه یا جملهٔ انگلیسی یا عربی ننویس.',
    'en': 'Write only in English. Do not use Persian or Arabic.',
    'ar': 'اكتب بالعربية فقط. لا تستخدم الفارسية أو الإنجليزية.',
    None: 'Reply in the language of the user message.',
}

ANSWER_FORMAT = {
    'fa': (
        'حداکثر پنج خط، بدون مقدمه و بدون فکر درونی. '
        'هیچ متنی بیرون این برچسب ننویس:\n<answer>\nپاسخ\n</answer>'
    ),
    'en': (
        'At most five lines. No preamble and no reasoning. '
        'Write nothing outside this tag:\n<answer>\nreply\n</answer>'
    ),
    'ar': (
        'خمس أسطر كحد أقصى، بلا مقدمة وبلا تفكير داخلي. '
        'لا تكتب شيئاً خارج هذه العلامة:\n<answer>\nالرد\n</answer>'
    ),
    None: (
        'At most five lines, in the user\'s language. '
        'Write nothing outside this tag:\n<answer>\nreply\n</answer>'
    ),
}

KNOWLEDGE_INSTRUCTIONS = {
    'hybrid': (
        'سؤال درباره همین مطب — خدمات، بیوگرافی و سوابق پزشک، آدرس، ساعت کار و تیم — '
        'را فقط از بخش «دانش مطب» جواب بده. '
        'اگر آن موضوع در دانش مطب نبود، بگو در سایت مطب نیامده و به تماس با مطب راهنمایی کن. '
        'فهرست فرضی خدمات یا سابقه نساز و آن را مال این مطب جا نزن. '
        'برای توضیح عمومی یک بیماری چشمی می‌توانی دانش عمومی بدهی و بگویی جایگزین معاینه نیست.'
    ),
    'rag_only': (
        'فقط از بخش «دانش مطب» پاسخ بده. اگر پاسخ در آن نبود بگو این مورد در اطلاعات مطب ثبت نشده '
        'و پیشنهاد تماس با مطب بده. از دانش عمومی مدل استفاده نکن و فهرست فرضی نساز.'
    ),
    'llm_only': (
        'از دانش خودت استفاده کن. فایل جداگانه‌ای در اختیار نداری. '
        'باز هم هیچ دارویی تجویز نکن.'
    ),
}

CONTINUITY = {
    'fa': 'اگر فقط سلام کرد یک جمله بگو. خودت را معرفی نکن. مستقیم به سؤال جواب بده.',
    'en': 'If the user only says hello, reply with one short sentence. Do not introduce yourself.',
    'ar': 'إذا سلّم فقط، أجب بجملة قصيرة. لا تعرّف بنفسك. أجب عن السؤال مباشرة.',
    None: 'If the user only says hello, reply with one short sentence in their language.',
}

SAFETY_BRIEF = {
    'fa': 'دارو تجویز نکن. تشخیص قطعی نده. اورژانس چشمی را به مطب ارجاع بده. تلفن و ساعت را فقط از دانش مطب بگو.',
    'en': 'Do not prescribe or diagnose. Send eye emergencies to the clinic. Take phone and hours only from the clinic notes.',
    'ar': 'لا تصف دواء ولا تشخّص. أحل طوارئ العين إلى العيادة. خذ الهاتف والساعات من معلومات العيادة فقط.',
    None: 'Do not prescribe or diagnose. Send eye emergencies to a clinic.',
}

_EN_HINTS = {
    'the', 'and', 'is', 'are', 'my', 'eye', 'what', 'how', 'when', 'have',
    'see', 'vision', 'pain', 'hello', 'please', 'can', 'you', 'your', 'with',
    'this', 'that', 'from', 'about', 'doctor',
}


def reply_language(question, page_language='fa'):
    """زبان پاسخ از روی متن همین پیام. خارج از فارسی و عربی و انگلیسی، None یعنی مدل خودش انتخاب کند."""
    text = question or ''
    page = page_language if page_language in ('fa', 'en', 'ar') else 'fa'
    fa_marks = len(re.findall(r'[پچژگ]', text))
    ar_marks = len(re.findall(r'[ةؤإأٱءئ]', text))
    arabic = len(re.findall(r'[\u0600-\u06FF]', text))
    latin = len(re.findall(r'[A-Za-z]', text))
    other = 0
    for char in text:
        if char.isspace() or char.isdigit():
            continue
        if '\u0600' <= char <= '\u06FF' or ('A' <= char <= 'Z') or ('a' <= char <= 'z'):
            continue
        if char.isalpha():
            other += 1
    if other >= 6 and other > arabic and other > latin:
        return None
    if arabic >= 3:
        if fa_marks and fa_marks >= ar_marks:
            return 'fa'
        if ar_marks and ar_marks > fa_marks:
            return 'ar'
        return page if page in ('fa', 'ar') else 'fa'
    if latin >= 8:
        words = set(re.findall(r'[a-z]+', text.lower()))
        if words & _EN_HINTS or page == 'en':
            return 'en'
        return None
    return page


def build_system_prompt(profile, language, question=''):
    page = language if language in DEFAULT_PROMPTS else 'fa'
    lang = reply_language(question, page) if question else page
    prompt_lang = lang if lang in DEFAULT_PROMPTS else page
    name = {
        'fa': profile.assistant_name_fa,
        'en': profile.assistant_name_en,
        'ar': profile.assistant_name_ar,
    }.get(prompt_lang) or profile.assistant_name_fa

    custom = {
        'fa': profile.prompt_fa,
        'en': profile.prompt_en,
        'ar': profile.prompt_ar,
    }.get(prompt_lang) or ''
    custom = (custom or '').strip() or DEFAULT_PROMPTS[prompt_lang].format(name=name)
    if '{name}' in custom:
        custom = custom.format(name=name)

    mode = profile.knowledge_mode or 'hybrid'
    mode_text = {
        'fa': {
            'hybrid': 'درباره مطب فقط از دانش مطب بگو. اگر نبود بگو در سایت نیست. علامت بیماری را کوتاه و بدون تشخیص بگو.',
            'rag_only': 'فقط از دانش مطب جواب بده. اگر نبود بگو ثبت نشده و تماس بگیرند.',
            'llm_only': 'از دانش عمومی جواب بده و دارو تجویز نکن.',
        },
        'en': {
            'hybrid': 'Use only the clinic notes for this clinic. If missing, say so. For symptoms, be brief and do not diagnose.',
            'rag_only': 'Answer only from the clinic notes. If missing, say it is not listed.',
            'llm_only': 'Use general knowledge. Do not prescribe.',
        },
        'ar': {
            'hybrid': 'عن العيادة استخدم معلومات العيادة فقط. إن غابت فقل ذلك. للأعراض أجب باختصار بلا تشخيص.',
            'rag_only': 'أجب من معلومات العيادة فقط. إن غابت فقل أنها غير مسجلة.',
            'llm_only': 'استخدم المعرفة العامة ولا تصف دواء.',
        },
    }.get(prompt_lang, {}).get(mode) or KNOWLEDGE_INSTRUCTIONS.get(mode, KNOWLEDGE_INSTRUCTIONS['hybrid'])
    lock = LANG_LOCK.get(lang, LANG_LOCK[None])
    continuity = CONTINUITY.get(lang, CONTINUITY[None])
    answer_format = ANSWER_FORMAT.get(lang, ANSWER_FORMAT[None])
    safety = SAFETY_BRIEF.get(lang, SAFETY_BRIEF[None])

    return (
        f'{lock}\n'
        f'{continuity}\n'
        f'{custom}\n'
        f'{safety}\n'
        f'{mode_text}\n'
        f'{answer_format}'
    )
