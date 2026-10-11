import logging

from .fallback import fallback_text
from .llm import build_chat_model
from .memory import DjangoConversationHistory, messages_for_model
from .prompts import build_system_prompt
from .rag import retrieve_context

logger = logging.getLogger('chatbot')


def _empty_rag(language):
    return {
        'fa': 'این مورد در اطلاعات ثبت‌شده مطب پیدا نشد. لطفاً با مطب تماس بگیرید.',
        'en': 'This is not in the clinic knowledge base. Please contact the office.',
        'ar': 'لا يوجد هذا الموضوع في معلومات العيادة. يرجى التواصل مع العيادة.',
    }[language]


def _llm_messages(profile, language, question, conversation=None, history=None):
    context = retrieve_context(profile, question)
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
        build_system_prompt(profile, language),
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
        result = llm.invoke(packed)
        text = (getattr(result, 'content', None) or '').strip()
        if not text:
            return polite, True, 'پاسخ مدل خالی بود.'
        return text, False, ''
    except Exception as exc:
        logger.exception('خطا در فراخوانی مدل چت')
        return polite, True, str(exc)


def _chunk_text(chunk):
    """متن قابل نمایش از پاسخ مدل؛ بعضی مدل‌ها به‌جای رشته، لیست می‌فرستند."""
    content = getattr(chunk, 'content', None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                parts.append(str(block.get('text') or block.get('content') or ''))
        return ''.join(parts)
    return ''


def stream_question(profile, language, question, history=None, conversation=None):
    """جریان پاسخ: وضعیت جستجو، سپس تکه‌های متن. اگر استریم خالی بود یک بار پاسخ کامل می‌گیرد."""
    language = language if language in ('fa', 'en', 'ar') else 'fa'
    polite = fallback_text(language)
    llm = build_chat_model(profile.active_llm)
    if llm is None:
        yield ('replace', polite, 'مدل فعال تنظیم نشده یا کلید خالی است.')
        return

    yield ('status', 'search', '')
    packed, early = _llm_messages(
        profile, language, question,
        conversation=conversation, history=history,
    )
    if early:
        yield ('status', 'write', '')
        yield ('delta', early, '')
        return

    yield ('status', 'write', '')
    got = []
    try:
        for chunk in llm.stream(packed):
            piece = _chunk_text(chunk)
            if piece:
                got.append(piece)
                yield ('delta', piece, '')
    except Exception as exc:
        logger.exception('خطا در استریم مدل چت')
        if not ''.join(got).strip():
            yield ('replace', polite, str(exc))
        return

    if ''.join(got).strip():
        return
    try:
        text = _chunk_text(llm.invoke(packed)).strip()
    except Exception as exc:
        logger.exception('خطا در دریافت پاسخ کامل')
        yield ('replace', polite, str(exc))
        return
    if not text:
        yield ('replace', polite, 'پاسخ مدل خالی بود.')
        return
    yield ('delta', text, '')
