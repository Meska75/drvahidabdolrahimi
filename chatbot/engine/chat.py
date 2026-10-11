import logging
import re

from .fallback import fallback_text
from .llm import build_chat_model, complete_text
from .memory import DjangoConversationHistory, messages_for_model
from .prompts import build_system_prompt
from .rag import retrieve_context

logger = logging.getLogger('chatbot')

_INTRO = {
    'fa': re.compile(
        r'^\s*(?:سلام(?:\s+و\s+وقت\s+بخیر)?[.،!\s]*)?'
        r'(?:من\s+)?دستیار(?:\s+هوش\s+مصنوعی)?[^.\n]{0,140}'
        r'(?:هستم|می‌باشم|ام)\s*[.!\n]+\s*'
    ),
    'en': re.compile(
        r"^\s*(?:Hello|Hi)[,!.\s]*(?:I am|I'm)\s+(?:the\s+)?(?:AI\s+)?assistant[^.\n]{0,160}\.\s*",
        re.I,
    ),
    'ar': re.compile(
        r'^\s*(?:مرحباً?|مرحبا|السلام عليكم)[^\n]{0,40}?أنا\s+مساعد[^.\n]{0,140}\.\s*'
    ),
}


def _empty_rag(language):
    return {
        'fa': 'این مورد در اطلاعات ثبت‌شده مطب پیدا نشد. لطفاً با مطب تماس بگیرید.',
        'en': 'This is not in the clinic knowledge base. Please contact the office.',
        'ar': 'لا يوجد هذا الموضوع في معلومات العيادة. يرجى التواصل مع العيادة.',
    }[language]


def asks_who_assistant(question):
    text = question or ''
    lowered = text.lower()
    needles = (
        'کی هستی', 'کیستی', 'کی هستید', 'اسم تو', 'اسمت', 'اسم شما',
        'خودت را معرفی', 'خودتو معرفی', 'who are you', 'your name',
        'من أنت', 'من انت', 'ما اسم',
    )
    return any(needle in text or needle in lowered for needle in needles)


def visible_reply(text, language, question):
    """معرفی تکراری ابتدای جواب را برمی‌دارد؛ سلام شروع گفتگو جدا نشان داده شده است."""
    from .llm import clean_for_user

    raw = clean_for_user(text)
    if asks_who_assistant(question):
        return raw.strip()
    pattern = _INTRO.get(language) or _INTRO['fa']
    cleaned = pattern.sub('', raw, count=1).strip()
    return cleaned or raw.strip()


def iter_visible(chunks, language, question):
    """اول جمله را نگه می‌دارد تا اگر معرفی تکراری بود حذف شود، بعد بقیه زنده می‌آید."""
    if asks_who_assistant(question):
        yield from chunks
        return
    buf = ''
    hold = True
    for chunk in chunks:
        if not hold:
            if chunk:
                yield chunk
            continue
        buf += chunk or ''
        ready = len(buf) >= 260 or (len(buf) >= 24 and re.search(r'[.!\n؟?]', buf))
        if not ready:
            continue
        hold = False
        cleaned = visible_reply(buf, language, question)
        if cleaned:
            yield cleaned
    if hold and buf:
        cleaned = visible_reply(buf, language, question)
        if cleaned:
            yield cleaned


def _llm_messages(profile, language, question, conversation=None, history=None):
    from .prompts import reply_language

    page = language if language in ('fa', 'en', 'ar') else 'fa'
    content_language = reply_language(question, page) or page
    context = retrieve_context(profile, question, language=content_language)
    if profile.knowledge_mode == 'rag_only' and not (context or '').strip():
        return None, _empty_rag(language)

    if conversation is not None:
        past = DjangoConversationHistory(conversation).messages
    else:
        from langchain_core.messages import AIMessage, HumanMessage
        past = []
        for item in history or []:
            if item.get('role') == 'user':
                past.append(HumanMessage(content=item.get('content', '')))
            else:
                past.append(AIMessage(content=item.get('content', '')))

    packed = messages_for_model(
        build_system_prompt(profile, language, question),
        context,
        past,
        question,
    )
    return packed, None


def answer_question(profile, language, question, history=None, conversation=None):
    language = language if language in ('fa', 'en', 'ar') else 'fa'
    polite = fallback_text(language)
    llm = build_chat_model(profile.active_llm)
    if llm is None:
        return polite, True, 'مدل فعال تنظیم نشده یا کلید خالی است.'

    packed, early = _llm_messages(
        profile, language, question,
        conversation=conversation, history=history,
    )
    if early:
        return early, False, ''
    try:
        text = visible_reply(complete_text(profile.active_llm, packed), language, question)
        if not text:
            return polite, True, 'پاسخ مدل خالی بود.'
        return text, False, ''
    except Exception as exc:
        logger.exception('خطا در فراخوانی مدل چت')
        return polite, True, str(exc)


def stream_question(profile, language, question, history=None, conversation=None):
    """جواب کامل مدل را می‌گیرد. نمایش تکه‌تکه در صفحه انجام می‌شود.

    استریم خود درگاه لیارا اتصال را نمی‌بندد و سرویس جواب را ناتمام قطع می‌کند.
    """
    language = language if language in ('fa', 'en', 'ar') else 'fa'
    polite = fallback_text(language)
    llm = build_chat_model(profile.active_llm)
    if llm is None:
        yield ('replace', polite, 'مدل فعال تنظیم نشده یا کلید خالی است.')
        return

    yield ('status', 'search', '')
    try:
        packed, early = _llm_messages(
            profile, language, question,
            conversation=conversation, history=history,
        )
    except Exception as exc:
        logger.exception('آماده‌سازی پیام چت ناموفق')
        packed = messages_for_model(
            build_system_prompt(profile, language, question), '', [], question,
        )
        early = None
        prepare_error = str(exc)
    else:
        prepare_error = ''

    if early:
        yield ('status', 'write', '')
        yield ('delta', early, '')
        return

    yield ('status', 'write', '')
    try:
        text = visible_reply(complete_text(profile.active_llm, packed), language, question)
    except Exception as exc:
        logger.exception('خطا در فراخوانی مدل چت')
        yield ('replace', polite, prepare_error or str(exc))
        return
    if not text:
        yield ('replace', polite, prepare_error or 'پاسخ مدل خالی بود.')
        return
    yield ('delta', text, '')
