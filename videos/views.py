from django.shortcuts import render
from django.db.models import Count, Q
from .models import VideoCategory, SiteVideo


def _video_context():
    videos = SiteVideo.objects.filter(is_published=True).select_related('category')
    categories = (
        VideoCategory.objects
        .annotate(video_count=Count('videos', filter=Q(videos__is_published=True)))
        .filter(video_count__gt=0)
        .order_by('sort_order', 'id')
    )
    return {
        'categories': categories,
        'videos': videos,
        'total_count': videos.count(),
        'cat_count': categories.count(),
    }


def persian_videos(request):
    return render(request, 'persian/persian_videos/video_list.html', _video_context())


def english_videos(request):
    return render(request, 'english/english_videos/video_list.html', _video_context())


def arabic_videos(request):
    return render(request, 'arabic/arabic_videos/video_list.html', _video_context())
