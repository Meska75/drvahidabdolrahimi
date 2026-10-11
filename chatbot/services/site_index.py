"""تبدیل محتوای زندهٔ سایت به قطعهٔ RAG — بدون پیام تماس و نظر بیمار."""

import html
import re
from pathlib import Path

from django.conf import settings
from django.utils.html import strip_tags

from chatbot.engine.rag import delete_chunks, replace_chunks

SITE_SOURCES = ('faq', 'services', 'doctor', 'clinic', 'team', 'blog')


def _clean(text):
    plain = strip_tags(text or '')
    plain = re.sub(r'\s+', ' ', plain).strip()
    return plain


def _pack(lang, label, parts):
    body = '\n'.join(part for part in parts if part)
    body = _clean(body)
    if not body:
        return None
    return f'[{label} / {lang}]\n{body}'


def chunks_for_instance(instance):
    """لیست (source_type, source_key, متن) برای یک رکورد سایت."""
    name = instance.__class__.__name__
    if name == 'FaqItem':
        return _faq(instance)
    if name == 'ServiceItem':
        return _service(instance)
    if name == 'DoctorEducation':
        return _education(instance)
    if name == 'DoctorAchievement':
        return _achievement(instance)
    if name == 'DoctorClinic':
        return _clinic(instance)
    if name == 'TeamMember':
        return _team(instance)
    if name == 'Post':
        return _post(instance)
    return []


def is_public(instance):
    name = instance.__class__.__name__
    if name == 'Post':
        return bool(instance.is_published)
    if hasattr(instance, 'is_active'):
        return bool(instance.is_active)
    return True


def source_type_of(instance):
    name = instance.__class__.__name__
    return {
        'FaqItem': 'faq',
        'ServiceItem': 'services',
        'DoctorEducation': 'doctor',
        'DoctorAchievement': 'doctor',
        'DoctorClinic': 'clinic',
        'TeamMember': 'team',
        'Post': 'blog',
    }.get(name, '')


def _faq(obj):
    rows = []
    key = f'faq-{obj.pk}'
    for lang, q, a in (
        ('fa', obj.question_fa, obj.answer_fa),
        ('en', obj.question_en, obj.answer_en),
        ('ar', obj.question_ar, obj.answer_ar),
    ):
        text = _pack(lang, 'سوال متداول', [q, a])
        if text:
            rows.append(('faq', key, text))
    return rows


def _service(obj):
    kind = 'خدمات جراحی' if obj.type == 'surgery' else 'خدمات مطب'
    rows = []
    key = f'service-{obj.pk}'
    for lang, title, summary, desc in (
        ('fa', obj.title_fa, obj.summary_fa, obj.description_fa),
        ('en', obj.title_en, obj.summary_en, obj.description_en),
        ('ar', obj.title_ar, obj.summary_ar, obj.description_ar),
    ):
        text = _pack(lang, kind, [title, summary, desc])
        if text:
            rows.append(('services', key, text))
    return rows


def _education(obj):
    rows = []
    key = f'education-{obj.pk}'
    for lang, degree, place in (
        ('fa', obj.degree_fa, obj.institution_fa),
        ('en', obj.degree_en, obj.institution_en),
        ('ar', obj.degree_ar, obj.institution_ar),
    ):
        text = _pack(lang, 'تحصیلات', [degree, place, obj.year])
        if text:
            rows.append(('doctor', key, text))
    return rows


def _achievement(obj):
    rows = []
    key = f'achievement-{obj.pk}'
    for lang, title in (
        ('fa', obj.title_fa),
        ('en', obj.title_en),
        ('ar', obj.title_ar),
    ):
        text = _pack(lang, 'افتخار', [title, obj.year])
        if text:
            rows.append(('doctor', key, text))
    return rows


def _clinic(obj):
    rows = []
    key = f'clinic-{obj.pk}'
    packs = (
        ('fa', obj.name_fa, obj.city_fa, obj.address_fa, obj.phone_1_fa, obj.phone_2_fa, obj.schedule_fa),
        ('en', obj.name_en, obj.city_en, obj.address_en, obj.phone_1_en, obj.phone_2_en, obj.schedule_en),
        ('ar', obj.name_ar, obj.city_ar, obj.address_ar, obj.phone_1_ar, obj.phone_2_ar, obj.schedule_ar),
    )
    for lang, name, city, address, phone1, phone2, schedule in packs:
        text = _pack(lang, 'مطب', [name, city, address, phone1, phone2, schedule])
        if text:
            rows.append(('clinic', key, text))
    return rows


def _team(obj):
    rows = []
    key = f'team-{obj.pk}'
    for lang, name, title, bio in (
        ('fa', obj.name_fa, obj.title_fa, obj.bio_fa),
        ('en', obj.name_en, obj.title_en, obj.bio_en),
        ('ar', obj.name_ar, obj.title_ar, obj.bio_ar),
    ):
        text = _pack(lang, 'تیم مطب', [name, title, bio])
        if text:
            rows.append(('team', key, text))
    return rows


def _post(obj):
    rows = []
    key = f'post-{obj.pk}'
    for lang, title, summary, content in (
        ('fa', obj.title_fa, obj.summary_fa, obj.content_fa),
        ('en', obj.title_en, obj.summary_en, obj.content_en),
        ('ar', obj.title_ar, obj.summary_ar, obj.content_ar),
    ):
        text = _pack(lang, 'مقاله', [title, summary, content])
        if text:
            rows.append(('blog', key, text))
    return rows


def profile_sources(profile):
    enabled = []
    for name in SITE_SOURCES:
        if getattr(profile, f'sync_site_{name}', False):
            enabled.append(name)
    return enabled


def remove_source(profile, source_type):
    return delete_chunks(profile, source_type=source_type)


def remove_item(profile, source_key):
    return delete_chunks(profile, source_key=source_key)


def write_rows(profile, rows):
    """ردیف‌های یک منبع را جایگزین می‌کند. rows خالی یعنی فقط حذف."""
    if not rows:
        return ''
    return replace_chunks(profile, [
        {
            'text': text,
            'source_type': source_type,
            'source_key': source_key,
            'source_label': source_key,
        }
        for source_type, source_key, text in rows
    ])


def sync_instance(profile, instance):
    source = source_type_of(instance)
    if source not in profile_sources(profile):
        return ''
    key_prefix = {
        'FaqItem': f'faq-{instance.pk}',
        'ServiceItem': f'service-{instance.pk}',
        'DoctorEducation': f'education-{instance.pk}',
        'DoctorAchievement': f'achievement-{instance.pk}',
        'DoctorClinic': f'clinic-{instance.pk}',
        'TeamMember': f'team-{instance.pk}',
        'Post': f'post-{instance.pk}',
    }.get(instance.__class__.__name__, '')
    if not is_public(instance):
        return remove_item(profile, key_prefix)
    return write_rows(profile, chunks_for_instance(instance))


def iter_source_queryset(source):
    if source == 'faq':
        from main.models import FaqItem
        return FaqItem.objects.filter(is_active=True)
    if source == 'services':
        from services.models import ServiceItem
        return ServiceItem.objects.filter(is_active=True)
    if source == 'doctor':
        from main.models import DoctorAchievement, DoctorEducation
        return list(DoctorEducation.objects.all()) + list(DoctorAchievement.objects.all())
    if source == 'clinic':
        from main.models import DoctorClinic
        return DoctorClinic.objects.filter(is_active=True)
    if source == 'team':
        from team.models import TeamMember
        return TeamMember.objects.filter(is_active=True)
    if source == 'blog':
        from blog.models import Post
        return Post.objects.filter(is_published=True)
    return []


def answer_sources(profile):
    """بخش‌های تیک‌خورده. اگر هیچ‌کدام روشن نباشد، محتوای عمومی سایت باز هم خوانده می‌شود."""
    chosen = profile_sources(profile)
    return chosen or list(SITE_SOURCES)


def _field(obj, name, language):
    value = getattr(obj, f'{name}_{language}', '') or ''
    if not str(value).strip() and language != 'fa':
        value = getattr(obj, f'{name}_fa', '') or ''
    return _clean(str(value))


def _tokens(text):
    stop = {
        'است', 'این', 'را', 'از', 'به', 'که', 'در', 'با', 'برای', 'چه', 'یا', 'و',
        'the', 'and', 'for', 'with', 'about', 'your', 'you',
    }
    return [
        token for token in re.findall(r'[\w\u0600-\u06FF]{2,}', (text or '').lower())
        if token not in stop
    ]


def _matching(lines, question, limit=24):
    tokens = set(_tokens(question))
    if not tokens:
        return list(lines)[:limit]
    scored = []
    for line in lines:
        overlap = len(tokens & set(_tokens(line)))
        if overlap:
            scored.append((overlap, line))
    if not scored:
        return []
    scored.sort(key=lambda item: item[0], reverse=True)
    return [line for _, line in scored[:limit]]


def _about_page_text(language):
    """بیوگرافی و تخصص‌های صفحه معرفی؛ این متن‌ها در دیتابیس نیستند."""
    relative = {
        'fa': 'templates/persian/persian_main/persian_about.html',
        'en': 'templates/english/english_main/english_about.html',
        'ar': 'templates/arabic/arabic_main/arabic_about.html',
    }.get(language)
    if not relative:
        return ''
    path = Path(settings.BASE_DIR) / relative
    if not path.is_file():
        return ''
    raw = path.read_text(encoding='utf-8')
    parts = []
    for marker in ('about-bio-section', 'about-expertise-section'):
        match = re.search(rf'<section class="{marker}"[^>]*>.*?</section>', raw, re.S)
        if not match:
            continue
        block = re.sub(r'\{%.*?%\}', ' ', match.group(0), flags=re.S)
        block = re.sub(r'\{\{.*?\}\}', ' ', block, flags=re.S)
        plain = _clean(html.unescape(strip_tags(block)))
        if plain:
            parts.append(plain)
    return '\n'.join(parts)[:2500]


def _service_block(language, question):
    from services.models import ServiceItem

    lines = []
    titles = []
    for item in ServiceItem.objects.filter(is_active=True).order_by('sort_order', 'id'):
        title = _field(item, 'title', language)
        if not title:
            continue
        kind = 'جراحی' if item.type == 'surgery' else 'مطب'
        desc = _field(item, 'description', language) or _field(item, 'summary', language)
        line = f'- {kind}: {title}' + (f' — {desc}' if desc else '')
        lines.append(line)
        titles.append(f'- {kind}: {title}')
    picked = _matching(lines, question)
    body = picked or titles
    if not body:
        return ''
    return 'خدمات این مطب:\n' + '\n'.join(body)


def _doctor_block(language):
    from main.models import DoctorAchievement, DoctorEducation

    parts = []
    about = _about_page_text(language)
    if about:
        parts.append('معرفی پزشک:\n' + about)
    education = []
    for item in DoctorEducation.objects.all().order_by('sort_order', 'id'):
        degree = _field(item, 'degree', language)
        place = _field(item, 'institution', language)
        year = _clean(str(item.year or ''))
        line = ' — '.join(bit for bit in (year, degree, place) if bit)
        if line:
            education.append('- ' + line)
    if education:
        parts.append('تحصیلات:\n' + '\n'.join(education))
    achievements = []
    for item in DoctorAchievement.objects.all().order_by('sort_order', 'id'):
        title = _field(item, 'title', language)
        year = _clean(str(item.year or ''))
        line = ' — '.join(bit for bit in (year, title) if bit)
        if line:
            achievements.append('- ' + line)
    if achievements:
        parts.append('افتخارات:\n' + '\n'.join(achievements))
    return '\n\n'.join(parts)


def _clinic_block(language):
    from main.models import DoctorClinic

    lines = []
    for item in DoctorClinic.objects.filter(is_active=True).order_by('sort_order', 'id'):
        bits = [
            _field(item, 'name', language),
            _field(item, 'city', language),
            _field(item, 'address', language),
            _field(item, 'phone_1', language),
            _field(item, 'phone_2', language),
            _field(item, 'schedule', language),
        ]
        line = ' — '.join(bit for bit in bits if bit)
        if line:
            lines.append('- ' + line)
    if not lines:
        return ''
    return 'مطب، آدرس و ساعت کار:\n' + '\n'.join(lines)


def _team_block(language, question):
    from team.models import TeamMember

    lines = []
    for item in TeamMember.objects.filter(is_active=True).order_by('sort_order', 'id'):
        bits = [
            _field(item, 'name', language),
            _field(item, 'title', language),
            _field(item, 'bio', language),
        ]
        line = ' — '.join(bit for bit in bits if bit)
        if line:
            lines.append('- ' + line)
    picked = _matching(lines, question) or lines[:12]
    if not picked:
        return ''
    return 'تیم مطب:\n' + '\n'.join(picked)


def _faq_block(language, question):
    from main.models import FaqItem

    lines = []
    for item in FaqItem.objects.filter(is_active=True).order_by('sort_order', 'id'):
        q = _field(item, 'question', language)
        a = _field(item, 'answer', language)
        if q or a:
            lines.append(f'س: {q}\nج: {a}')
    picked = _matching(lines, question, limit=6) or lines[:6]
    if not picked:
        return ''
    return 'پرسش‌های متداول:\n' + '\n\n'.join(picked)


def _blog_block(language, question):
    from blog.models import Post

    lines = []
    for item in Post.objects.filter(is_published=True).order_by('-id'):
        title = _field(item, 'title', language)
        summary = _field(item, 'summary', language)
        line = ' — '.join(bit for bit in (title, summary) if bit)
        if line:
            lines.append('- ' + line)
    picked = _matching(lines, question, limit=3) or lines[:3]
    if not picked:
        return ''
    return 'مقالات:\n' + '\n'.join(picked)


def live_site_context(profile, language, question, limit=6500):
    """متن فعلی سایت، بدون وابستگی به embedding. اگر ایندکس RAG خالی باشد همین مبناست."""
    language = language if language in ('fa', 'en', 'ar') else 'fa'
    sources = set(answer_sources(profile))
    blocks = []
    if 'doctor' in sources:
        block = _doctor_block(language)
        if block:
            blocks.append(block)
    if 'services' in sources:
        block = _service_block(language, question)
        if block:
            blocks.append(block)
    if 'clinic' in sources:
        block = _clinic_block(language)
        if block:
            blocks.append(block)
    if 'team' in sources:
        block = _team_block(language, question)
        if block:
            blocks.append(block)
    if 'faq' in sources:
        block = _faq_block(language, question)
        if block:
            blocks.append(block)
    if 'blog' in sources:
        block = _blog_block(language, question)
        if block:
            blocks.append(block)
    return '\n\n'.join(blocks)[:limit]


def sync_profile_sources(profile, sources=None):
    """بخش‌های انتخاب‌شده را از نو می‌نویسد و بخش‌های خاموش را از RAG برمی‌دارد."""
    chosen = sources if sources is not None else profile_sources(profile)
    errors = []
    for source in SITE_SOURCES:
        if source not in chosen:
            err = remove_source(profile, source)
            if err:
                errors.append(err)
            continue
        err = remove_source(profile, source)
        if err:
            errors.append(f'{source}: {err}')
            continue
        rows = []
        for item in iter_source_queryset(source):
            rows.extend(chunks_for_instance(item))
        err = write_rows(profile, rows)
        if err:
            errors.append(f'{source}: {err}')
    return errors
