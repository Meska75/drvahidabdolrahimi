from django.contrib import admin
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
    list_display = ('title_fa', 'category', 'source_type', 'platform', 'is_published', 'sort_order')
    list_editable = ('is_published', 'sort_order')
    list_filter = ('is_published', 'source_type', 'platform', 'category')
    search_fields = ('title_fa', 'title_en')
    fieldsets = (
        ('فارسی', {'fields': ('title_fa', 'description_fa')}),
        ('English', {'fields': ('title_en', 'description_en'), 'classes': ('collapse',)}),
        ('العربية', {'fields': ('title_ar', 'description_ar'), 'classes': ('collapse',)}),
        ('منبع ویدیو', {'fields': ('category', 'source_type', 'platform', 'file_path', 'embed_code')}),
        ('رسانه', {'fields': ('thumbnail', 'duration_sec')}),
        ('انتشار', {'fields': ('is_published', 'published_at', 'sort_order', 'views_count')}),
    )

    class Media:
        js = ('js/admin_video_fields.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['description_fa'].widget = RTL
        form.base_fields['description_en'].widget = LTR
        form.base_fields['description_ar'].widget = RTL
        return form
