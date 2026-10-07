"""کپچای تصویری فرم تماس — روی خود سرور ساخته می‌شود و به گوگل وابسته نیست."""

import base64
import hashlib
import hmac
import io
import os
import secrets
import time

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

# بدون صفر، او، یک و آی تا با هم قاطی نشوند
ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
CODE_LENGTH = 5
TTL_SECONDS = 60 * 15
SESSION_KEY = 'contact_captcha'

_DIGIT_FOLD = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')

_FONT_CANDIDATES = (
    r'C:\Windows\Fonts\arialbd.ttf',
    r'C:\Windows\Fonts\arial.ttf',
    r'C:\Windows\Fonts\tahoma.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
)


def normalize(value):
    """فاصله و ارقام فارسی/عربی را کنار می‌گذارد."""
    return ''.join((value or '').translate(_DIGIT_FOLD).split()).upper()


def _digest(code):
    return hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        normalize(code).encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()


def _font(size):
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default(size=size)


def render_image(code):
    """تصویر کد را به صورت data URI برمی‌گرداند."""
    width, height = 220, 68
    image = Image.new('RGB', (width, height), (241, 245, 249))
    draw = ImageDraw.Draw(image)
    rng = secrets.SystemRandom()
    for _ in range(5):
        draw.line(
            [
                (rng.randint(0, width), rng.randint(0, height)),
                (rng.randint(0, width), rng.randint(0, height)),
            ],
            fill=(148, 163, 184),
            width=1,
        )
    font = _font(34)
    x = 14
    for char in code:
        glyph = Image.new('RGBA', (42, 54), (0, 0, 0, 0))
        ImageDraw.Draw(glyph).text((2, 0), char, font=font, fill=(15, 42, 82, 255))
        rotated = glyph.rotate(rng.randint(-14, 14), expand=True, resample=Image.Resampling.BICUBIC)
        image.paste(rotated, (x, rng.randint(2, 12)), rotated)
        x += 38
    for _ in range(35):
        draw.point(
            (rng.randint(0, width - 1), rng.randint(0, height - 1)),
            fill=(100, 116, 139),
        )
    buffer = io.BytesIO()
    image.save(buffer, format='PNG', optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return f'data:image/png;base64,{encoded}'


def remember(session, code):
    """برای تست: کد مشخص را در نشست ذخیره می‌کند."""
    session[SESSION_KEY] = {'digest': _digest(code), 'ts': time.time()}
    session.modified = True


def new_captcha(session):
    """کد تازه می‌سازد، در نشست می‌گذارد و تصویر را برمی‌گرداند."""
    code = ''.join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
    remember(session, code)
    return render_image(code)


def matches(session, answer):
    """جواب را با کد نشست مقایسه می‌کند و همان کد را می‌سوزاند."""
    payload = session.pop(SESSION_KEY, None) or {}
    session.modified = True
    expected = payload.get('digest') or ''
    try:
        fresh = (time.time() - float(payload.get('ts') or 0)) <= TTL_SECONDS
    except (TypeError, ValueError):
        fresh = False
    if not expected or not fresh or not answer:
        return False
    return hmac.compare_digest(expected, _digest(answer))
