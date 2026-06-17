from django.shortcuts import render, redirect
from django.db.models import Q
from .models import FaqItem, PatientTestimonial


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

    faqs = FaqItem.objects.filter(is_active=True)[:6]
    testimonials = PatientTestimonial.objects.order_by('sort_order', '-created_at')[:6]
    response = render(request, 'persian/persian_main/persian_home.html', {
        'faqs': faqs,
        'testimonials': testimonials,
    })
    response.set_cookie('dr_lang', 'fa', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def persian_about(request):
    return render(request, 'persian/persian_main/persian_about.html')


def persian_contact(request):
    return render(request, 'persian/persian_main/persian_contact.html')


def persian_faq(request):
    faqs = FaqItem.objects.filter(is_active=True).order_by('category', 'sort_order', 'id')
    return render(request, 'persian/persian_main/persian_faq.html', {'faqs': faqs})


def english_home(request):
    faqs = FaqItem.objects.filter(is_active=True)[:6]
    testimonials = PatientTestimonial.objects.order_by('sort_order', '-created_at')[:6]
    response = render(request, 'english/english_main/english_home.html', {
        'faqs': faqs,
        'testimonials': testimonials,
    })
    response.set_cookie('dr_lang', 'en', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def english_about(request):
    return render(request, 'english/english_main/english_about.html')


def english_contact(request):
    return render(request, 'english/english_main/english_contact.html')


def english_faq(request):
    faqs = FaqItem.objects.filter(is_active=True).order_by('category', 'sort_order', 'id')
    return render(request, 'english/english_main/english_faq.html', {'faqs': faqs})


def arabic_home(request):
    faqs = FaqItem.objects.filter(is_active=True)[:6]
    testimonials = PatientTestimonial.objects.order_by('sort_order', '-created_at')[:6]
    response = render(request, 'arabic/arabic_main/arabic_home.html', {
        'faqs': faqs,
        'testimonials': testimonials,
    })
    response.set_cookie('dr_lang', 'ar', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def arabic_about(request):
    return render(request, 'arabic/arabic_main/arabic_about.html')


def arabic_contact(request):
    return render(request, 'arabic/arabic_main/arabic_contact.html')


def arabic_faq(request):
    faqs = FaqItem.objects.filter(is_active=True).order_by('category', 'sort_order', 'id')
    return render(request, 'arabic/arabic_main/arabic_faq.html', {'faqs': faqs})


# ===== جستجو =====

def _search_db(query, lang):
    """جستجو در تمام مدل‌های محتوایی — لیست‌ها برمی‌گردانند نه QuerySet."""
    from blog.models import Post
    from services.models import ServiceItem
    from videos.models import SiteVideo
    from team.models import TeamMember

    # فیلدهای اصلی بر اساس زبان، همراه fallback به فارسی
    if lang == 'en':
        post_q    = Q(title_en__icontains=query) | Q(summary_en__icontains=query) | Q(title_fa__icontains=query)
        service_q = Q(title_en__icontains=query) | Q(description_en__icontains=query) | Q(title_fa__icontains=query)
        faq_q     = Q(question_en__icontains=query) | Q(answer_en__icontains=query) | Q(question_fa__icontains=query)
        video_q   = Q(title_en__icontains=query) | Q(description_en__icontains=query) | Q(title_fa__icontains=query)
        team_q    = Q(name_en__icontains=query) | Q(title_en__icontains=query) | Q(name_fa__icontains=query)
    elif lang == 'ar':
        post_q    = Q(title_ar__icontains=query) | Q(summary_ar__icontains=query) | Q(title_fa__icontains=query)
        service_q = Q(title_ar__icontains=query) | Q(description_ar__icontains=query) | Q(title_fa__icontains=query)
        faq_q     = Q(question_ar__icontains=query) | Q(answer_ar__icontains=query) | Q(question_fa__icontains=query)
        video_q   = Q(title_ar__icontains=query) | Q(description_ar__icontains=query) | Q(title_fa__icontains=query)
        team_q    = Q(name_ar__icontains=query) | Q(title_ar__icontains=query) | Q(name_fa__icontains=query)
    else:  # fa
        post_q    = Q(title_fa__icontains=query) | Q(summary_fa__icontains=query) | Q(title_en__icontains=query)
        service_q = Q(title_fa__icontains=query) | Q(description_fa__icontains=query) | Q(title_en__icontains=query)
        faq_q     = Q(question_fa__icontains=query) | Q(answer_fa__icontains=query) | Q(question_en__icontains=query)
        video_q   = Q(title_fa__icontains=query) | Q(description_fa__icontains=query) | Q(title_en__icontains=query)
        team_q    = Q(name_fa__icontains=query) | Q(title_fa__icontains=query) | Q(name_en__icontains=query)

    posts    = list(Post.objects.filter(is_published=True).filter(post_q).distinct()[:8])
    services = list(ServiceItem.objects.filter(is_active=True).filter(service_q).distinct()[:6])
    faqs     = list(FaqItem.objects.filter(is_active=True).filter(faq_q).distinct()[:6])
    videos   = list(SiteVideo.objects.filter(is_published=True).filter(video_q).distinct()[:6])
    team     = list(TeamMember.objects.filter(is_active=True).filter(team_q).distinct()[:4])

    return posts, services, faqs, videos, team


def persian_search(request):
    query = request.GET.get('q', '').strip()
    posts = services = faqs = videos = team = []
    total = 0
    if query and len(query) >= 2:
        posts, services, faqs, videos, team = _search_db(query, 'fa')
        total = len(posts) + len(services) + len(faqs) + len(videos) + len(team)
    return render(request, 'persian/persian_main/persian_search.html', {
        'query': query, 'posts': posts, 'services': services,
        'faqs': faqs, 'videos': videos, 'team': team, 'total': total,
    })


def english_search(request):
    query = request.GET.get('q', '').strip()
    posts = services = faqs = videos = team = []
    total = 0
    if query and len(query) >= 2:
        posts, services, faqs, videos, team = _search_db(query, 'en')
        total = len(posts) + len(services) + len(faqs) + len(videos) + len(team)
    return render(request, 'english/english_main/english_search.html', {
        'query': query, 'posts': posts, 'services': services,
        'faqs': faqs, 'videos': videos, 'team': team, 'total': total,
    })


def arabic_search(request):
    query = request.GET.get('q', '').strip()
    posts = services = faqs = videos = team = []
    total = 0
    if query and len(query) >= 2:
        posts, services, faqs, videos, team = _search_db(query, 'ar')
        total = len(posts) + len(services) + len(faqs) + len(videos) + len(team)
    return render(request, 'arabic/arabic_main/arabic_search.html', {
        'query': query, 'posts': posts, 'services': services,
        'faqs': faqs, 'videos': videos, 'team': team, 'total': total,
    })
