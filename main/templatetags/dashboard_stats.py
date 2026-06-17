import json
from django import template
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Count

register = template.Library()

_MONTHS_FA = {
    1: 'ژانویه', 2: 'فوریه', 3: 'مارس',
    4: 'آوریل', 5: 'مه', 6: 'ژوئن',
    7: 'ژوئیه', 8: 'اوت', 9: 'سپتامبر',
    10: 'اکتبر', 11: 'نوامبر', 12: 'دسامبر',
}


@register.simple_tag
def get_dashboard_stats():
    """آمار مورد نیاز داشبورد ادمین"""
    from main.models import ContactMessage, PatientTestimonial
    from blog.models import Post, Comment
    from gallery.models import GalleryImage
    from videos.models import SiteVideo
    from team.models import TeamMember
    from services.models import ServiceItem

    unread_messages  = ContactMessage.objects.filter(is_read=False).count()
    pending_comments = Comment.objects.filter(is_approved=False).count()
    pending_opinions = PatientTestimonial.objects.filter(is_approved=False).count()

    published_posts  = Post.objects.filter(is_published=True).count()
    total_posts      = Post.objects.count()
    gallery_images   = GalleryImage.objects.filter(is_active=True).count()
    published_videos = SiteVideo.objects.filter(is_published=True).count()
    total_videos     = SiteVideo.objects.count()
    team_members     = TeamMember.objects.filter(is_active=True).count()
    services_count   = ServiceItem.objects.count()

    # ---- داده نمودار ۱: توزیع محتوا (دونات) ----
    dist_labels = json.dumps(
        ['مقالات منتشرشده', 'تصاویر گالری', 'ویدیوها', 'اعضای تیم', 'خدمات'],
        ensure_ascii=False
    )
    dist_data = json.dumps([
        published_posts, gallery_images, published_videos,
        team_members, services_count
    ])

    # ---- داده نمودار ۲: مقالات ماهانه ۶ ماه اخیر (ستونی) ----
    six_ago = timezone.now() - timedelta(days=180)
    monthly_qs = (
        Post.objects.filter(is_published=True, published_at__gte=six_ago)
        .annotate(month=TruncMonth('published_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    monthly_labels = json.dumps(
        [_MONTHS_FA[r['month'].month] for r in monthly_qs],
        ensure_ascii=False
    )
    monthly_counts = json.dumps([r['count'] for r in monthly_qs])

    # ---- داده نمودار ۳: محبوب‌ترین مقالات (افقی) ----
    top_posts_qs = (
        Post.objects.filter(is_published=True, views_count__gt=0)
        .order_by('-views_count')[:6]
        .values('title_fa', 'views_count')
    )
    top_labels = json.dumps(
        [p['title_fa'][:28] + ('…' if len(p['title_fa']) > 28 else '')
         for p in top_posts_qs],
        ensure_ascii=False
    )
    top_views = json.dumps([p['views_count'] for p in top_posts_qs])

    return {
        'unread_messages':  unread_messages,
        'pending_comments': pending_comments,
        'pending_opinions': pending_opinions,
        'total_alerts':     unread_messages + pending_comments + pending_opinions,

        'published_posts':  published_posts,
        'total_posts':      total_posts,
        'draft_posts':      total_posts - published_posts,
        'gallery_images':   gallery_images,
        'published_videos': published_videos,
        'total_videos':     total_videos,
        'team_members':     team_members,
        'services':         services_count,

        'recent_messages': ContactMessage.objects.filter(is_read=False)
                                          .order_by('-created_at')[:6],
        'recent_comments': Comment.objects.filter(is_approved=False)
                                   .select_related('post')
                                   .order_by('-created_at')[:6],

        # چارت‌ها
        'chart_dist_labels':   dist_labels,
        'chart_dist_data':     dist_data,
        'chart_monthly_labels': monthly_labels,
        'chart_monthly_counts': monthly_counts,
        'chart_top_labels':    top_labels,
        'chart_top_views':     top_views,
    }
