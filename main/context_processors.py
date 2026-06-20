from .models import DoctorClinic, SiteSetting, SocialLinks


def site_context(request):
    """داده‌های جهانی سایت — در تمام قالب‌ها قابل استفاده"""
    try:
        main_clinic = DoctorClinic.objects.filter(is_active=True).order_by('sort_order').first()
    except Exception:
        main_clinic = None

    try:
        site_settings = {s.key: s for s in SiteSetting.objects.all()}
    except Exception:
        site_settings = {}

    try:
        social_links = SocialLinks.objects.filter(pk=1).first()
    except Exception:
        social_links = None

    return {
        'main_clinic': main_clinic,
        'site_settings': site_settings,
        'social_links': social_links,
    }
