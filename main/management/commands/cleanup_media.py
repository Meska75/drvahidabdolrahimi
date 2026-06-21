"""
دستور مدیریتی برای پاک‌سازی فایل‌های media بی‌صاحب (orphan).
استفاده:
    python manage.py cleanup_media          # فقط گزارش
    python manage.py cleanup_media --delete # حذف واقعی
"""
import pathlib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models as django_models

# نگاشت پوشه → مدل و فیلد
FIELD_MAP = [
    ('banners',            'main',     'SiteBanner',   'image'),
    ('clinics',            'main',     'DoctorClinic',  'image'),
    ('services',           'services', 'ServiceItem',  'image'),
    ('blog',               'blog',     'Post',         'image'),
    ('gallery',            'gallery',  'GalleryImage', 'image'),
    ('team',               'team',     'TeamMember',   'photo'),
    ('videos/thumbnails',  'videos',   'SiteVideo',    'thumbnail'),
    ('videos',             'videos',   'SiteVideo',    'file_path'),
]


def _db_files(app_label, model_name, field_name):
    """فایل‌های ثبت‌شده در دیتابیس برای یک فیلد را برمی‌گرداند."""
    from django.apps import apps
    model = apps.get_model(app_label, model_name)
    qs = model.objects.exclude(**{f'{field_name}__exact': ''}).values_list(field_name, flat=True)
    return set(v for v in qs if v)


class Command(BaseCommand):
    help = 'فایل‌های media بی‌صاحب را شناسایی و (در صورت تأیید) حذف می‌کند.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='فایل‌های بی‌صاحب را واقعاً حذف کن (بدون این flag فقط گزارش نمایش داده می‌شود).',
        )

    def handle(self, *args, **options):
        media_root = pathlib.Path(settings.MEDIA_ROOT)
        do_delete = options['delete']

        total_orphans = 0
        total_size = 0

        for folder, app, model_name, field in FIELD_MAP:
            folder_path = media_root / folder
            if not folder_path.exists():
                continue

            # فایل‌های روی دیسک (فقط یک سطح — بدون زیرپوشه برای جلوگیری از تداخل)
            disk = {
                str(f.relative_to(media_root)).replace('\\', '/')
                for f in folder_path.iterdir()
                if f.is_file()
            }

            db = _db_files(app, model_name, field)
            orphans = disk - db

            if not orphans:
                self.stdout.write(self.style.SUCCESS(f'✓  {folder}/ — همه فایل‌ها معتبرند'))
                continue

            self.stdout.write(self.style.WARNING(f'\n📁  {folder}/'))
            for orphan in sorted(orphans):
                fpath = media_root / orphan
                size_kb = fpath.stat().st_size / 1024
                total_size += fpath.stat().st_size
                total_orphans += 1
                self.stdout.write(f'   • {orphan}  ({size_kb:.0f} KB)')

                if do_delete:
                    fpath.unlink()
                    self.stdout.write(self.style.ERROR('     → حذف شد'))

        self.stdout.write('\n' + '─' * 50)
        if do_delete:
            self.stdout.write(self.style.SUCCESS(
                f'✔  {total_orphans} فایل بی‌صاحب حذف شد — {total_size/1024:.0f} KB آزاد شد.'
            ))
        else:
            if total_orphans:
                self.stdout.write(self.style.WARNING(
                    f'⚠  {total_orphans} فایل بی‌صاحب یافت شد ({total_size/1024:.0f} KB).'
                ))
                self.stdout.write('برای حذف اجرا کنید:  python manage.py cleanup_media --delete')
            else:
                self.stdout.write(self.style.SUCCESS('✔  هیچ فایل بی‌صاحبی وجود ندارد.'))
