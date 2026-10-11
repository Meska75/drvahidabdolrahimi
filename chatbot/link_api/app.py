"""نسخه لینک — سایت دیگر دکتر با کلید پروفایل به همین موتور وصل می‌شود."""

import os
import re
import sys
import uuid
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.conf import settings as django_settings

if not django_settings.configured:
    django.setup()

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from django.utils import timezone

from chatbot.engine.chat import answer_question
from chatbot.engine.greetings import ensure_stored_greeting, greeting_text
from chatbot.engine.memory import DjangoConversationHistory
from chatbot.models import ChatbotProfile, ChatMessage, Conversation
from chatbot.protect.rate_limit import allow_message
from chatbot.services.secrets import decrypt_secret

app = FastAPI(
    title='دستیار پزشک — نسخه لینک',
    description='هر پروفایل پرامپت، مدل و RAG جدا دارد. اگر در پنل «محتوای سایت» روشن باشد، همان قطعات در این API هم جستجو می‌شوند.',
    version='1.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['POST', 'GET', 'OPTIONS'],
    allow_headers=['*'],
)


class SessionIn(BaseModel):
    language: str = 'fa'
    session_id: str | None = Field(
        default=None,
        description='شناسه پایدار مرورگر (localStorage). اگر خالی باشد ساخته می‌شود.',
    )


class ChatIn(SessionIn):
    message: str = Field(..., min_length=1, max_length=2000)


def memory_days():
    return int(getattr(django_settings, 'CHATBOT_MEMORY_DAYS', 7))


def normalize_session_id(raw):
    """هر بازدیدکننده باید شناسهٔ خودش را داشته باشد — anonymous مشترک ممنوع است."""
    value = (raw or '').strip()
    if value.lower() in ('', 'anonymous', 'null', 'undefined'):
        return uuid.uuid4().hex
    if not re.fullmatch(r'[A-Za-z0-9_-]{16,64}', value):
        return uuid.uuid4().hex
    return value[:64]


def profile_from_key(key: str):
    if not key:
        return None
    for profile in ChatbotProfile.objects.filter(link_enabled=True):
        stored = decrypt_secret(profile.link_api_key_encrypted)
        if stored and stored == key:
            return profile
    return None


def check_origin(profile, origin: str):
    allowed = profile.origin_list()
    if not allowed:
        return True
    if not origin:
        return False
    origin = origin.rstrip('/')
    return origin in allowed


def require_profile(x_chatbot_key: str, origin: str):
    profile = profile_from_key(x_chatbot_key)
    if profile is None:
        raise HTTPException(status_code=401, detail='unauthorized')
    if not check_origin(profile, origin):
        raise HTTPException(status_code=403, detail='origin not allowed')
    return profile


def lang_of(value):
    return value if value in ('fa', 'en', 'ar') else 'fa'


def assistant_name(profile, language):
    return {
        'fa': profile.assistant_name_fa,
        'en': profile.assistant_name_en,
        'ar': profile.assistant_name_ar,
    }[language]


def serialized_messages(conv):
    return list(conv.messages.order_by('created_at').values('role', 'content'))


def get_link_conversation(profile, session_id, language, ip):
    cutoff = timezone.now() - timedelta(days=memory_days())
    Conversation.objects.filter(
        profile=profile, source='link', updated_at__lt=cutoff,
    ).delete()
    conv = Conversation.objects.filter(
        profile=profile, session_key=session_id, source='link', language=language,
    ).order_by('-updated_at').first()
    if conv and conv.updated_at < cutoff:
        conv.delete()
        conv = None
    if conv is None:
        conv = Conversation.objects.create(
            profile=profile,
            session_key=session_id,
            source='link',
            language=language,
            ip_address=ip,
        )
    return conv


def ensure_greeting(conv, profile, language):
    ensure_stored_greeting(
        conv, greeting_text(language, assistant_name(profile, language)),
    )


@app.get('/health')
def health():
    return {'ok': True, 'memory_days': memory_days()}


@app.post('/v1/chat')
def chat(
    payload: ChatIn,
    x_chatbot_key: str = Header(default=''),
    origin: str = Header(default=''),
    x_forwarded_for: str = Header(default=''),
):
    profile = require_profile(x_chatbot_key, origin)
    language = lang_of(payload.language)
    session_id = normalize_session_id(payload.session_id)
    ip = (x_forwarded_for.split(',')[0].strip() if x_forwarded_for else '0.0.0.0')
    if not allow_message(profile, ip):
        text = {
            'fa': 'لطفاً کمی صبر کنید و دوباره پیام بفرستید.',
            'en': 'Please wait a moment and try again.',
            'ar': 'يرجى الانتظار قليلاً ثم المحاولة مرة أخرى.',
        }[language]
        return {'session_id': session_id, 'reply': text, 'memory_days': memory_days()}

    conv = get_link_conversation(profile, session_id, language, ip)
    ChatMessage.objects.create(conversation=conv, role='user', content=payload.message)
    reply, used_fallback, internal = answer_question(
        profile, language, payload.message, conversation=conv,
    )
    ChatMessage.objects.create(
        conversation=conv,
        role='assistant',
        content=reply,
        used_fallback=used_fallback,
        internal_error=internal,
    )
    return {
        'session_id': session_id,
        'reply': reply,
        'memory_days': memory_days(),
    }


@app.post('/v1/greeting')
def greeting(
    payload: SessionIn,
    x_chatbot_key: str = Header(default=''),
    origin: str = Header(default=''),
    x_forwarded_for: str = Header(default=''),
):
    profile = require_profile(x_chatbot_key, origin)
    language = lang_of(payload.language)
    session_id = normalize_session_id(payload.session_id)
    ip = (x_forwarded_for.split(',')[0].strip() if x_forwarded_for else '0.0.0.0')
    conv = get_link_conversation(profile, session_id, language, ip)
    ensure_greeting(conv, profile, language)
    return {
        'session_id': session_id,
        'greeting': greeting_text(language, assistant_name(profile, language)),
        'messages': serialized_messages(conv),
        'memory_days': memory_days(),
    }


@app.post('/v1/history')
def history(
    payload: SessionIn,
    x_chatbot_key: str = Header(default=''),
    origin: str = Header(default=''),
    x_forwarded_for: str = Header(default=''),
):
    profile = require_profile(x_chatbot_key, origin)
    language = lang_of(payload.language)
    session_id = normalize_session_id(payload.session_id)
    ip = (x_forwarded_for.split(',')[0].strip() if x_forwarded_for else '0.0.0.0')
    conv = get_link_conversation(profile, session_id, language, ip)
    return {
        'session_id': session_id,
        'messages': serialized_messages(conv),
        'memory_days': memory_days(),
    }


@app.post('/v1/clear')
def clear(
    payload: SessionIn,
    x_chatbot_key: str = Header(default=''),
    origin: str = Header(default=''),
    x_forwarded_for: str = Header(default=''),
):
    profile = require_profile(x_chatbot_key, origin)
    language = lang_of(payload.language)
    session_id = normalize_session_id(payload.session_id)
    ip = (x_forwarded_for.split(',')[0].strip() if x_forwarded_for else '0.0.0.0')
    conv = get_link_conversation(profile, session_id, language, ip)
    DjangoConversationHistory(conv).clear()
    ensure_greeting(conv, profile, language)
    return {
        'session_id': session_id,
        'messages': serialized_messages(conv),
        'memory_days': memory_days(),
    }
