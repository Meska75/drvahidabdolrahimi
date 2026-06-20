from django.shortcuts import render, redirect
from django.db.models import Q
from .models import (
    FaqItem, PatientTestimonial, ContactMessage,
    DoctorEducation, DoctorAchievement, DoctorClinic, SiteBanner,
)
from .forms import ContactMessageForm
from team.models import TeamMember
from services.models import ServiceItem
from gallery.models import GalleryImage


def _detect_lang(request):
    """زبان اولیه مرورگر را از هدر Accept-Language استخراج می‌کند."""
    header = request.META.get('HTTP_ACCEPT_LANGUAGE', '').lower()
    primary = header.split(',')[0].split(';')[0].strip()
    if primary.startswith('ar'):
        return 'ar'
    if primary.startswith('en'):
        return 'en'
    return 'fa'


def _service_context():
    """داده‌های خدمات و تیم برای صفحه اصلی — کاروسل‌ها."""
    return {
        'office_items': ServiceItem.objects.filter(type='office', is_active=True)[:6],
        'surgery_items': ServiceItem.objects.filter(type='surgery', is_active=True)[:6],
        'team_members': TeamMember.objects.filter(is_active=True),
    }


def _about_context():
    """داده‌های مشترک صفحه درباره در هر سه زبان."""
    return {
        'educations': DoctorEducation.objects.all(),
        'achievements': DoctorAchievement.objects.all(),
        'clinics': DoctorClinic.objects.filter(is_active=True),
    }


def persian_home(request):
    if 'dr_lang' not in request.COOKIES:
        lang = _detect_lang(request)
        if lang == 'ar':
            return redirect('/ar/')
        if lang == 'en':
            return redirect('/en/')

    faqs = FaqItem.objects.filter(is_active=True)[:6]
    testimonials = PatientTestimonial.objects.order_by('sort_order', '-created_at')[:6]
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('sort_order')[:8]
    banners = SiteBanner.objects.filter(location='home_hero', is_active=True).order_by('sort_order')
    ctx = _service_context()
    ctx.update({
        'faqs': faqs,
        'testimonials': testimonials,
        'gallery_images': gallery_images,
        'banners': banners,
    })
    response = render(request, 'persian/persian_main/persian_home.html', ctx)
    response.set_cookie('dr_lang', 'fa', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def persian_about(request):
    return render(request, 'persian/persian_main/persian_about.html', _about_context())


def persian_contact(request):
    form = ContactMessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ContactMessage.objects.create(
            full_name=form.cleaned_data['name'],
            phone=form.cleaned_data.get('phone', ''),
            email=form.cleaned_data.get('email', ''),
            subject=form.cleaned_data.get('subject', ''),
            message=form.cleaned_data['message'],
            language='fa',
        )
        return redirect(request.path + '?sent=1')
    return render(request, 'persian/persian_main/persian_contact.html', {
        'sent': request.GET.get('sent') == '1',
    })


def persian_faq(request):
    faqs = FaqItem.objects.filter(is_active=True).order_by('category', 'sort_order', 'id')
    return render(request, 'persian/persian_main/persian_faq.html', {'faqs': faqs})


def english_home(request):
    faqs = FaqItem.objects.filter(is_active=True)[:6]
    testimonials = PatientTestimonial.objects.order_by('sort_order', '-created_at')[:6]
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('sort_order')[:8]
    banners = SiteBanner.objects.filter(location='home_hero', is_active=True).order_by('sort_order')
    ctx = _service_context()
    ctx.update({
        'faqs': faqs,
        'testimonials': testimonials,
        'gallery_images': gallery_images,
        'banners': banners,
    })
    response = render(request, 'english/english_main/english_home.html', ctx)
    response.set_cookie('dr_lang', 'en', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def english_about(request):
    return render(request, 'english/english_main/english_about.html', _about_context())


def english_contact(request):
    form = ContactMessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ContactMessage.objects.create(
            full_name=form.cleaned_data['name'],
            phone=form.cleaned_data.get('phone', ''),
            email=form.cleaned_data.get('email', ''),
            subject=form.cleaned_data.get('subject', ''),
            message=form.cleaned_data['message'],
            language='en',
        )
        return redirect(request.path + '?sent=1')
    return render(request, 'english/english_main/english_contact.html', {
        'sent': request.GET.get('sent') == '1',
    })


def english_faq(request):
    faqs = FaqItem.objects.filter(is_active=True).order_by('category', 'sort_order', 'id')
    return render(request, 'english/english_main/english_faq.html', {'faqs': faqs})


def arabic_home(request):
    faqs = FaqItem.objects.filter(is_active=True)[:6]
    testimonials = PatientTestimonial.objects.order_by('sort_order', '-created_at')[:6]
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('sort_order')[:8]
    banners = SiteBanner.objects.filter(location='home_hero', is_active=True).order_by('sort_order')
    ctx = _service_context()
    ctx.update({
        'faqs': faqs,
        'testimonials': testimonials,
        'gallery_images': gallery_images,
        'banners': banners,
    })
    response = render(request, 'arabic/arabic_main/arabic_home.html', ctx)
    response.set_cookie('dr_lang', 'ar', max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response


def arabic_about(request):
    return render(request, 'arabic/arabic_main/arabic_about.html', _about_context())


def arabic_contact(request):
    form = ContactMessageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ContactMessage.objects.create(
            full_name=form.cleaned_data['name'],
            phone=form.cleaned_data.get('phone', ''),
            email=form.cleaned_data.get('email', ''),
            subject=form.cleaned_data.get('subject', ''),
            message=form.cleaned_data['message'],
            language='ar',
        )
        return redirect(request.path + '?sent=1')
    return render(request, 'arabic/arabic_main/arabic_contact.html', {
        'sent': request.GET.get('sent') == '1',
    })


def arabic_faq(request):
    faqs = FaqItem.objects.filter(is_active=True).order_by('category', 'sort_order', 'id')
    return render(request, 'arabic/arabic_main/arabic_faq.html', {'faqs': faqs})


# ===== جستجو =====

def _search_db(query, lang):
    """جستجو در تمام مدل‌های محتوایی — لیست‌ها برمی‌گردانند نه QuerySet."""
    from blog.models import Post
    from videos.models import SiteVideo

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
