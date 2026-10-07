"""وقتی مدل وصل نیست، متن مودبانه — بدون اشاره به قطعی مدل یا API."""

FALLBACK = {
    'fa': (
        'ممنون از پیام شما. در حال حاضر امکان پاسخ‌گویی آنلاین فراهم نیست. '
        'لطفاً از بخش تماس با ما پیام بگذارید یا با مطب تماس بگیرید.'
    ),
    'en': (
        'Thank you for your message. Online replies are not available at the moment. '
        'Please use the contact page or call the clinic.'
    ),
    'ar': (
        'شكراً لرسالتك. الرد عبر المحادثة غير متاح حالياً. '
        'يرجى استخدام صفحة الاتصال أو الاتصال بالعيادة.'
    ),
}


def fallback_text(language):
    return FALLBACK.get(language) or FALLBACK['fa']
