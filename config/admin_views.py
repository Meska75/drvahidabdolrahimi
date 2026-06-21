from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from utils.storage_stats import get_media_stats


@staff_member_required
def storage_stats_view(request):
    context = {
        'title': 'آمار فضای ذخیره‌سازی',
        'stats': get_media_stats(),
    }
    return render(request, 'admin/storage_stats.html', context)
