"""تبدیل محتوای زندهٔ سایت به قطعهٔ RAG — بدون پیام تماس و نظر بیمار."""

import logging
import re

from django.utils.html import strip_tags

from chatbot.engine.rag import get_vectorstore

logger = logging.getLogger('chatbot')

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


def _delete_where(store, where):
    try:
        store._collection.delete(where=where)
    except Exception:
        logger.exception('حذف قطعهٔ سایت از Chroma ناموفق')


def remove_source(profile, source_type):
    store = get_vectorstore(profile)
    if store is None:
        return 'اتصال embedding فعال نیست.'
    _delete_where(store, {'source_type': source_type, 'profile': profile.slug})
    return ''


def remove_item(profile, source_key):
    store = get_vectorstore(profile)
    if store is None:
        return 'اتصال embedding فعال نیست.'
    _delete_where(store, {'source_key': source_key, 'profile': profile.slug})
    return ''


def write_rows(profile, rows):
    """ردیف‌های یک منبع را جایگزین می‌کند. rows خالی یعنی فقط حذف."""
    if not rows:
        return ''
    store = get_vectorstore(profile)
    if store is None:
        return 'اتصال embedding فعال نیست.'
    keys = {row[1] for row in rows}
    for key in keys:
        _delete_where(store, {'source_key': key, 'profile': profile.slug})
    texts = []
    metadatas = []
    ids = []
    for index, (source_type, source_key, text) in enumerate(rows):
        texts.append(text)
        metadatas.append({
            'source': source_key,
            'source_type': source_type,
            'source_key': source_key,
            'profile': profile.slug,
            'file_id': f'site-{source_key}',
        })
        ids.append(f'site-{profile.slug}-{source_key}-{index}')
    store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    return ''


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
