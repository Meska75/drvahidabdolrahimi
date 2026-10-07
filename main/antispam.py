"""لایه‌های احتیاطی فرم تماس، کنار کپچا و فیلد تله."""

import re
import time
from datetime import timedelta

from django.core.signing import (
    BadSignature,
    SignatureExpired,
    Signer,
    TimestampSigner,
    b62_decode,
    b62_encode,
)
from django.utils import timezone

SIGNER = TimestampSigner(salt='contact-opened')
MIN_SECONDS = 3
MAX_AGE_SECONDS = 60 * 60 * 2
RATE_WINDOW = timedelta(minutes=10)
RATE_MAX = 2
NAME_WINDOW = timedelta(minutes=30)
# از چهارمین نام تکراری در این بازه، پیام اسپم حساب می‌شود
NAME_REPEAT_LIMIT = 3

PHONE_ERRORS = {
    'fa': 'شماره تماس را مثل ۰۹۱۲۱۲۳۴۵۶۷ یا تلفن ثابت با کد شهر وارد کنید.',
}
RATE_ERRORS = {
    'fa': 'چند پیام پشت‌سرهم فرستاده شده. لطفاً چند دقیقه صبر کنید و کد تازهٔ تصویر را وارد کنید.',
    'en': 'Several messages were sent in a row. Please wait a few minutes and enter the new image code.',
    'ar': 'أُرسلت عدة رسائل متتالية. انتظر بضع دقائق وأدخل رمز الصورة الجديد.',
}
EXPIRED_ERRORS = {
    'fa': 'این صفحه مدت زیادی باز مانده. کد تازهٔ تصویر را وارد کنید و دوباره بفرستید.',
    'en': 'This page has been open too long. Enter the new image code and send again.',
    'ar': 'بقيت هذه الصفحة مفتوحة طويلاً. أدخل رمز الصورة الجديد وأعد الإرسال.',
}

_DIGIT_FOLD = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')


def client_ip(request):
    """آی‌پی بازدیدکننده؛ پشت nginx همان X-Forwarded-For است."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()[:45]
    return (request.META.get('REMOTE_ADDR') or '')[:45]


def issue_opened_at(when=None):
    """مهر زمان امضاشدهٔ لحظهٔ باز شدن فرم. when برای تست است."""
    if when is None:
        return SIGNER.sign('ok')
    base = Signer(salt='contact-opened')
    stamped = 'ok%s%s' % (base.sep, b62_encode(int(when)))
    return base.sign(stamped)


def opening_status(token):
    """وضعیت مهر زمان: ok، too_fast، expired یا invalid."""
    if not token:
        return 'invalid'
    try:
        SIGNER.unsign(token, max_age=MAX_AGE_SECONDS)
    except SignatureExpired:
        return 'expired'
    except BadSignature:
        return 'invalid'
    try:
        issued = b62_decode(token.rsplit(SIGNER.sep, 2)[-2])
    except (IndexError, ValueError, TypeError):
        return 'invalid'
    if (time.time() - issued) < MIN_SECONDS:
        return 'too_fast'
    return 'ok'


def normalize_phone(value):
    text = (value or '').translate(_DIGIT_FOLD)
    return re.sub(r'[\s\-\(\)\.]', '', text)


def persian_phone_ok(value):
    """شمارهٔ خالی مجاز است. شمارهٔ پر باید موبایل یا تلفن ایران باشد."""
    raw = normalize_phone(value)
    if not raw:
        return True
    phone = raw
    if phone.startswith('0098'):
        phone = '0' + phone[4:]
    elif phone.startswith('+98'):
        phone = '0' + phone[3:]
    elif phone.startswith('98') and len(phone) >= 12:
        phone = '0' + phone[2:]
    if re.fullmatch(r'9\d{9}', phone):
        phone = '0' + phone
    return re.fullmatch(r'0\d{10}', phone) is not None


def name_key(name):
    return ' '.join((name or '').split()).casefold()


def repeated_name(name):
    """همان نام در نیم‌ساعت اخیر چند بار آمده باشد."""
    from .models import ContactMessage

    key = name_key(name)
    if len(key) < 2:
        return False
    since = timezone.now() - NAME_WINDOW
    recent = ContactMessage.objects.filter(created_at__gte=since).values_list('full_name', flat=True)
    count = sum(1 for item in recent if name_key(item) == key)
    return count >= NAME_REPEAT_LIMIT


def rate_limited(ip):
    """بیش از دو پیام ذخیره‌شده از یک آی‌پی در ده دقیقه."""
    from .models import ContactMessage

    if not ip:
        return False
    since = timezone.now() - RATE_WINDOW
    count = ContactMessage.objects.filter(ip_address=ip, created_at__gte=since).count()
    return count >= RATE_MAX
