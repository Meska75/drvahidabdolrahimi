from django.contrib import admin
from django.utils.html import format_html
from .models import SiteBannerProxy, DoctorPhoto, BuildingPhoto, ClinicInteriorPhoto


@admin.register(SiteBannerProxy)
class SiteBannerAdmin(admin.ModelAdmin):
    list_display = ('preview', 'get_location_display', 'caption_fa', 'sort_order', 'is_active')
    list_filter = ('location', 'is_active')
    list_editable = ('sort_order', 'is_active')
    ordering = ('location', 'sort_order')
    fieldsets = (
        ('تصویر', {
            'fields': ('location', 'image', 'is_active', 'sort_order'),
        }),
        ('متن (اختیاری)', {
            'classes': ('collapse',),
            'fields': ('caption_fa', 'caption_en', 'caption_ar',
                       'alt_fa', 'alt_en', 'alt_ar'),
        }),
    )

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return '—'

    @admin.display(description='موقعیت')
    def get_location_display(self, obj):
        return obj.get_location_display()


@admin.register(DoctorPhoto)
class DoctorPhotoAdmin(admin.ModelAdmin):
    list_display = ('preview', 'type', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    fieldsets = (
        ('تصویر', {
            'description': 'هر نوع فقط یک تصویر فعال می‌تواند داشته باشد.',
            'fields': ('type', 'image', 'is_active'),
        }),
        ('متن Alt (SEO)', {
            'classes': ('collapse',),
            'fields': ('alt_fa', 'alt_en', 'alt_ar'),
        }),
    )

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:56px;border-radius:50%;object-fit:cover;" />',
                obj.image.url
            )
        return '—'


@admin.register(BuildingPhoto)
class BuildingPhotoAdmin(admin.ModelAdmin):
    list_display = ('preview', 'caption_fa', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    ordering = ('sort_order',)
    fieldsets = (
        ('تصویر', {
            'fields': ('image', 'is_active', 'sort_order'),
        }),
        ('توضیحات', {
            'classes': ('collapse',),
            'fields': ('caption_fa', 'caption_en', 'caption_ar'),
        }),
    )

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return '—'


@admin.register(ClinicInteriorPhoto)
class ClinicInteriorPhotoAdmin(admin.ModelAdmin):
    list_display = ('preview', 'caption_fa', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    ordering = ('sort_order',)
    fieldsets = (
        ('تصویر', {
            'fields': ('image', 'is_active', 'sort_order'),
        }),
        ('توضیحات', {
            'classes': ('collapse',),
            'fields': ('caption_fa', 'caption_en', 'caption_ar'),
        }),
    )

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;border-radius:6px;object-fit:cover;" />',
                obj.image.url
            )
        return '—'
