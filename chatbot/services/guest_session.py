import re
import uuid
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from chatbot.models import Conversation
from chatbot.protect.rate_limit import client_ip

COOKIE_NAME = 'dr_chat_id'
MEMORY_DAYS = getattr(settings, 'CHATBOT_MEMORY_DAYS', 7)


def guest_id_from_request(request):
    raw = (request.COOKIES.get(COOKIE_NAME) or '').strip().lower()
    if re.fullmatch(r'[a-f0-9]{32}', raw):
        return raw
    return uuid.uuid4().hex


def attach_guest_cookie(response, guest_id):
    """کوکی ۷روزه جدا از نشست لاگین — بدون ساخت اکانت."""
    max_age = MEMORY_DAYS * 24 * 60 * 60
    response.set_cookie(
        COOKIE_NAME,
        guest_id,
        max_age=max_age,
        httponly=True,
        samesite='Lax',
        secure=not settings.DEBUG,
        path='/',
    )
    return response


def purge_stale_conversations(profile, source='widget'):
    cutoff = timezone.now() - timedelta(days=MEMORY_DAYS)
    Conversation.objects.filter(
        profile=profile,
        source=source,
        updated_at__lt=cutoff,
    ).delete()


def get_or_create_guest_conversation(request, profile, language, source='widget'):
    guest_id = guest_id_from_request(request)
    purge_stale_conversations(profile, source=source)
    cutoff = timezone.now() - timedelta(days=MEMORY_DAYS)
    conv = Conversation.objects.filter(
        profile=profile,
        session_key=guest_id,
        source=source,
    ).first()
    if conv and conv.updated_at < cutoff:
        conv.delete()
        conv = None
    if conv is None:
        conv = Conversation.objects.create(
            profile=profile,
            session_key=guest_id,
            source=source,
            language=language,
            ip_address=client_ip(request),
        )
    elif conv.language != language:
        conv.language = language
        conv.save(update_fields=['language', 'updated_at'])
    return conv, guest_id
