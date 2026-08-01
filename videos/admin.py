from django.contrib import admin
from django.utils.html import format_html
from ckeditor.widgets import CKEditorWidget
from .models import VideoCategory, SiteVideo

RTL = CKEditorWidget(config_name='rtl')
LTR = CKEditorWidget(config_name='ltr')


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'slug', 'sort_order')
    list_editable = ('sort_order',)
    prepopulated_fields = {'slug': ('name_fa',)}


@admin.register(SiteVideo)
class SiteVideoAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title_fa', 'category', 'source_type', 'platform', 'is_published', 'sort_order')
    list_editable = ('is_published', 'sort_order')
    list_filter = ('is_published', 'source_type', 'platform', 'category')
    search_fields = ('title_fa', 'title_en')
    fieldsets = (
        ('فارسی', {'fields': ('title_fa', 'description_fa')}),
        ('English', {'fields': ('title_en', 'description_en'), 'classes': ('collapse',)}),
        ('العربية', {'fields': ('title_ar', 'description_ar'), 'classes': ('collapse',)}),
        ('منبع ویدیو', {
            'description': 'برای آپلود فایل ویدیو، «نوع منبع» را روی «آپلود مستقیم» بگذارید. فیلد «تصویر بند انگشتی» فقط برای عکس پیش‌نمایش است.',
            'fields': ('category', 'source_type', 'platform', 'file_path', 'embed_code'),
        }),
        ('رسانه', {'fields': ('thumbnail', 'duration_sec')}),
        ('انتشار', {'fields': ('is_published', 'published_at', 'sort_order', 'views_count')}),
    )

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width:72px;height:50px;object-fit:cover;'
                'border-radius:6px;border:1px solid #475569;display:block;">',
                obj.thumbnail.url
            )
        icons = {'youtube': '▶ YouTube', 'aparat': '▶ آپارات', 'direct': '📁 فایل'}
        label = icons.get(obj.platform, '🎬 ویدیو')
        return format_html(
            '<span style="background:#334155;color:#94a3b8;padding:3px 10px;'
            'border-radius:6px;font-size:0.78rem;white-space:nowrap;">{}</span>',
            label
        )

    class Media:
        js = ('js/admin_video_fields.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['description_fa'].widget = RTL
        form.base_fields['description_en'].widget = LTR
        form.base_fields['description_ar'].widget = RTL
        # فیلتر انتخاب فایل: فقط فرمت‌های ویدیو (نه تصویر)
        form.base_fields['file_path'].widget.attrs['accept'] = (
            'video/mp4,video/webm,video/ogg,video/quicktime,'
            '.mp4,.webm,.ogg,.mov,.avi,.mkv,.m4v'
        )
        form.base_fields['file_path'].help_text = (
            'ابتدا «نوع منبع» را روی «آپلود مستقیم» بگذارید. '
            'فقط فایل ویدیو (mp4, webm, mov, …) — حداکثر ۵۰ MB'
        )
        # تصویر بند انگشتی فقط برای پیش‌نمایش است
        if 'thumbnail' in form.base_fields:
            form.base_fields['thumbnail'].widget.attrs['accept'] = 'image/*'
            form.base_fields['thumbnail'].help_text = (
                'تصویر پیش‌نمایش کارت ویدیو (نه فایل ویدیو) — حداکثر ۵ MB'
            )
        return form
