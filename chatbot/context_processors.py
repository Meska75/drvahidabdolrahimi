from chatbot.models import ChatbotProfile


def chatbot_widget(request):
    """اگر پروفایل پیش‌فرض روشن باشد، ویجت در صفحات سایت تزریق می‌شود."""
    profile = None
    try:
        profile = ChatbotProfile.default()
    except Exception:
        profile = None
    path = request.path or '/'
    if path.startswith('/en/') or path == '/en':
        language = 'en'
        direction = 'ltr'
    elif path.startswith('/ar/') or path == '/ar':
        language = 'ar'
        direction = 'rtl'
    else:
        language = 'fa'
        direction = 'rtl'
    return {
        'chatbot_enabled': bool(profile and profile.widget_enabled),
        'chatbot_language': language,
        'chatbot_direction': direction,
        'chatbot_profile': profile,
    }
