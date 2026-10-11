import json

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

from chatbot.engine.chat import answer_question, stream_question
from chatbot.engine.fallback import fallback_text
from chatbot.engine.greetings import ensure_stored_greeting, greeting_text
from chatbot.engine.memory import DjangoConversationHistory
from chatbot.models import ChatbotProfile, ChatMessage
from chatbot.protect.bot_detect import honeypot_filled, issue_token, token_is_too_fast, token_is_valid
from chatbot.protect.rate_limit import allow_message, client_ip
from chatbot.services.guest_session import (
    attach_guest_cookie,
    get_or_create_guest_conversation,
    guest_id_from_request,
)


def _language_from_path(path):
    if path.startswith('/en/') or path == '/en':
        return 'en'
    if path.startswith('/ar/') or path == '/ar':
        return 'ar'
    return 'fa'


def _profile_or_none():
    return ChatbotProfile.default()


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


def _assistant_name(profile, language):
    return {
        'fa': profile.assistant_name_fa,
        'en': profile.assistant_name_en,
        'ar': profile.assistant_name_ar,
    }.get(language) or profile.assistant_name_fa


def _json(data, guest_id, status=200):
    response = JsonResponse(data, status=status)
    return attach_guest_cookie(response, guest_id)


def _serialized_messages(conv):
    return list(conv.messages.order_by('created_at').values('role', 'content'))


def _ensure_greeting(conv, language, profile):
    text = greeting_text(language, _assistant_name(profile, language))
    ensure_stored_greeting(conv, text)


@require_GET
@ensure_csrf_cookie
def widget_config(request):
    profile = _profile_or_none()
    language = request.GET.get('lang') or _language_from_path(request.path)
    if language not in ('fa', 'en', 'ar'):
        language = _language_from_path(request.META.get('HTTP_REFERER', '') or '/')
        if language not in ('fa', 'en', 'ar'):
            language = 'fa'
    enabled = bool(profile and profile.widget_enabled)
    guest_id = guest_id_from_request(request)
    payload = {
        'enabled': enabled,
        'language': language,
        'token': issue_token() if enabled else '',
        'name': _assistant_name(profile, language) if profile else '',
        'greeting': greeting_text(language, _assistant_name(profile, language)) if profile else '',
        'memory_days': 7,
    }
    return _json(payload, guest_id)


@require_POST
def start_chat(request):
    profile = _profile_or_none()
    data = _json_body(request)
    language = data.get('language') or 'fa'
    if language not in ('fa', 'en', 'ar'):
        language = 'fa'
    guest_id = guest_id_from_request(request)

    if not profile or not profile.widget_enabled:
        return _json({'ok': False, 'enabled': False}, guest_id, status=404)

    if honeypot_filled(data):
        return _json({
            'ok': True,
            'messages': [{
                'role': 'assistant',
                'content': greeting_text(language, _assistant_name(profile, language)),
            }],
            'token': issue_token(),
        }, guest_id)

    conv, guest_id = get_or_create_guest_conversation(request, profile, language)
    _ensure_greeting(conv, language, profile)
    return _json({
        'ok': True,
        'messages': _serialized_messages(conv),
        'token': issue_token(),
    }, guest_id)


@require_POST
def clear_chat(request):
    profile = _profile_or_none()
    data = _json_body(request)
    language = data.get('language') if data.get('language') in ('fa', 'en', 'ar') else 'fa'
    guest_id = guest_id_from_request(request)
    if not profile or not profile.widget_enabled:
        return _json({'ok': False, 'enabled': False}, guest_id, status=404)
    conv, guest_id = get_or_create_guest_conversation(request, profile, language)
    DjangoConversationHistory(conv).clear()
    _ensure_greeting(conv, language, profile)
    return _json({
        'ok': True,
        'messages': _serialized_messages(conv),
        'token': issue_token(),
    }, guest_id)


def _guard(request, data, profile):
    language = data.get('language') or 'fa'
    polite = fallback_text(language if language in ('fa', 'en', 'ar') else 'fa')
    if honeypot_filled(data):
        return polite
    token = data.get('token') or ''
    if not token_is_valid(token) or token_is_too_fast(token):
        return polite
    ip = client_ip(request)
    if not allow_message(profile, ip):
        return {
            'fa': 'لطفاً کمی صبر کنید و دوباره پیام بفرستید.',
            'en': 'Please wait a moment and try again.',
            'ar': 'يرجى الانتظار قليلاً ثم المحاولة مرة أخرى.',
        }.get(language, polite)
    return None


@require_POST
def send_message(request):
    profile = _profile_or_none()
    data = _json_body(request)
    language = data.get('language') if data.get('language') in ('fa', 'en', 'ar') else 'fa'
    question = (data.get('message') or '').strip()
    guest_id = guest_id_from_request(request)

    if not profile or not profile.widget_enabled:
        return _json({'ok': False, 'enabled': False}, guest_id, status=404)
    if not question:
        return _json({'ok': False, 'error': 'empty'}, guest_id, status=400)
    if len(question) > 2000:
        question = question[:2000]

    blocked = _guard(request, data, profile)
    conv, guest_id = get_or_create_guest_conversation(request, profile, language)
    ChatMessage.objects.create(conversation=conv, role='user', content=question)

    if blocked:
        ChatMessage.objects.create(
            conversation=conv, role='assistant', content=blocked, used_fallback=True,
        )
        return _json({'ok': True, 'reply': blocked, 'token': issue_token()}, guest_id)

    reply, used_fallback, internal = answer_question(
        profile, language, question, conversation=conv,
    )
    ChatMessage.objects.create(
        conversation=conv,
        role='assistant',
        content=reply,
        used_fallback=used_fallback,
        internal_error=internal,
    )
    return _json({'ok': True, 'reply': reply, 'token': issue_token()}, guest_id)


@require_POST
def stream_message(request):
    profile = _profile_or_none()
    data = _json_body(request)
    language = data.get('language') if data.get('language') in ('fa', 'en', 'ar') else 'fa'
    question = (data.get('message') or '').strip()[:2000]
    guest_id = guest_id_from_request(request)

    if not profile or not profile.widget_enabled:
        return _json({'ok': False, 'enabled': False}, guest_id, status=404)
    if not question:
        return _json({'ok': False, 'error': 'empty'}, guest_id, status=400)

    blocked = _guard(request, data, profile)
    conv, guest_id = get_or_create_guest_conversation(request, profile, language)
    ChatMessage.objects.create(conversation=conv, role='user', content=question)

    def event_stream():
        full = []
        used_fallback = False
        internal = ''
        if blocked:
            yield f'data: {json.dumps({"token": blocked}, ensure_ascii=False)}\n\n'
            full.append(blocked)
            used_fallback = True
        else:
            for piece, fb, err in stream_question(
                profile, language, question, conversation=conv,
            ):
                if err:
                    internal = err
                if fb:
                    used_fallback = True
                    full = [piece]
                    yield f'data: {json.dumps({"token": piece, "reset": True}, ensure_ascii=False)}\n\n'
                else:
                    full.append(piece)
                    yield f'data: {json.dumps({"token": piece}, ensure_ascii=False)}\n\n'
        text = ''.join(full)
        ChatMessage.objects.create(
            conversation=conv,
            role='assistant',
            content=text,
            used_fallback=used_fallback,
            internal_error=internal,
        )
        yield f'data: {json.dumps({"done": True, "token": issue_token()})}\n\n'

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return attach_guest_cookie(response, guest_id)
