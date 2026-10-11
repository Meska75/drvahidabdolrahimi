import time

from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

SIGNER = TimestampSigner(salt='chatbot-widget')
MIN_SECONDS_BEFORE_SEND = 1.2


def issue_token():
    return SIGNER.sign('ok')


def token_is_valid(token):
    if not token:
        return False
    try:
        SIGNER.unsign(token, max_age=60 * 60 * 6)
        return True
    except (BadSignature, SignatureExpired):
        return False


def token_is_too_fast(token):
    """ربات‌هایی که بلافاصله بعد از گرفتن توکن پیام می‌فرستند."""
    if not token:
        return True
    try:
        # TimestampSigner مقدار را به شکل value:timestamp:sig نگه می‌دارد
        parts = token.rsplit(':', 2)
        if len(parts) < 3:
            return True
        from django.core.signing import b62_decode
        issued = b62_decode(parts[-2])
        return (time.time() - issued) < MIN_SECONDS_BEFORE_SEND
    except Exception:
        return True


def honeypot_filled(data):
    """فیلد پنهان؛ انسان آن را خالی می‌گذارد."""
    value = (data.get('dr_hp') or data.get('website') or data.get('company_url') or '').strip()
    return bool(value)
