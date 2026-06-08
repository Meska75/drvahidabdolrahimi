from django.shortcuts import render, redirect


def _detect_lang(request):
    """زبان اولیه مرورگر را از هدر Accept-Language استخراج می‌کند."""
    header = request.META.get('HTTP_ACCEPT_LANGUAGE', '').lower()
    primary = header.split(',')[0].split(';')[0].strip()
    if primary.startswith('ar'):
        return 'ar'
    if primary.startswith('en'):
        return 'en'
    return 'fa'


def persian_home(request):
    # اگر کاربر هنوز زبانی انتخاب نکرده، بر اساس مرورگر redirect کن
    if 'dr_lang' not in request.COOKIES:
        lang = _detect_lang(request)
        if lang == 'ar':
            return redirect('/ar/')
        if lang == 'en':
            return redirect('/en/')

    response = render(request, 'persian/persian_main/persian_home.html')
    response.set_cookie('dr_lang', 'fa', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def persian_about(request):
    return render(request, 'persian/persian_main/persian_about.html')


def persian_contact(request):
    return render(request, 'persian/persian_main/persian_contact.html')


def english_home(request):
    response = render(request, 'english/english_main/english_home.html')
    # ثبت انتخاب کاربر — دیگر auto-redirect نخواهد شد
    response.set_cookie('dr_lang', 'en', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def english_about(request):
    return render(request, 'english/english_main/english_about.html')


def english_contact(request):
    return render(request, 'english/english_main/english_contact.html')


def arabic_home(request):
    response = render(request, 'arabic/arabic_main/arabic_home.html')
    # ثبت انتخاب کاربر — دیگر auto-redirect نخواهد شد
    response.set_cookie('dr_lang', 'ar', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def arabic_about(request):
    return render(request, 'arabic/arabic_main/arabic_about.html')


def arabic_contact(request):
    return render(request, 'arabic/arabic_main/arabic_contact.html')
