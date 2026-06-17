from django.shortcuts import render
from django.db.models import Count, Q
from .models import GalleryTag, GalleryImage


def _gallery_context():
    images = GalleryImage.objects.filter(is_active=True).prefetch_related('tags')
    tags = (
        GalleryTag.objects
        .annotate(image_count=Count('images', filter=Q(images__is_active=True)))
        .filter(image_count__gt=0)
        .order_by('sort_order', 'id')
    )
    return {
        'tags': tags,
        'images': images,
        'total_count': images.count(),
        'tag_count': tags.count(),
    }


def persian_gallery(request):
    return render(request, 'persian/persian_gallery/gallery.html', _gallery_context())


def english_gallery(request):
    return render(request, 'english/english_gallery/gallery.html', _gallery_context())


def arabic_gallery(request):
    return render(request, 'arabic/arabic_gallery/gallery.html', _gallery_context())
