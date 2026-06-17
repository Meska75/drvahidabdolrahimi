from django.contrib import admin
from .models import GalleryTag, GalleryImage


@admin.register(GalleryTag)
class GalleryTagAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_en', 'slug', 'sort_order')
    list_editable = ('sort_order',)
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'sort_order', 'created_at')
    list_editable = ('is_active', 'sort_order')
    filter_horizontal = ('tags',)
    search_fields = ('title_fa', 'title_en')
    fieldsets = (
        ('تصویر', {'fields': ('image', 'is_active', 'sort_order', 'tags')}),
        ('فارسی', {'fields': ('title_fa', 'description_fa', 'alt_fa')}),
        ('English', {'fields': ('title_en', 'description_en', 'alt_en'), 'classes': ('collapse',)}),
        ('العربية', {'fields': ('title_ar', 'description_ar', 'alt_ar'), 'classes': ('collapse',)}),
    )
