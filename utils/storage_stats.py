import os
from pathlib import Path
from django.conf import settings


def _folder_stats(path: Path) -> dict:
    """حجم و تعداد فایل‌های یک پوشه را محاسبه می‌کند."""
    total_bytes = 0
    count = 0
    if path.exists():
        for f in path.rglob('*'):
            if f.is_file():
                total_bytes += f.stat().st_size
                count += 1
    return {'bytes': total_bytes, 'count': count}


def get_media_stats() -> dict:
    """آمار کامل پوشه media را برمی‌گرداند."""
    media_root = Path(settings.MEDIA_ROOT)

    folders = {
        'بنرها':           'banners',
        'مقالات (بلاگ)':   'blog',
        'گالری تصاویر':    'gallery',
        'خدمات':           'services',
        'تیم پزشکی':       'team',
        'ویدیوها':         'videos',
        'مطب / کلینیک':   'clinics',
    }

    rows = []
    grand_total = 0
    for label, folder in folders.items():
        stats = _folder_stats(media_root / folder)
        grand_total += stats['bytes']
        rows.append({
            'label':  label,
            'folder': folder,
            'bytes':  stats['bytes'],
            'size':   _human(stats['bytes']),
            'count':  stats['count'],
        })

    # سایر فایل‌ها (CKEditor uploads و غیره)
    other = _folder_stats(media_root) ['bytes'] - grand_total
    if other < 0:
        other = 0
    grand_total_with_other = grand_total + other

    return {
        'rows':        rows,
        'total_bytes': grand_total_with_other,
        'total_size':  _human(grand_total_with_other),
    }


def _human(size_bytes: int) -> str:
    """تبدیل bytes به فرمت خوانا."""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size_bytes < 1024:
            return f'{size_bytes:.1f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.1f} TB'
