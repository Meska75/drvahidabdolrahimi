from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from .models import Category, Post, Comment

RTL = CKEditorWidget(config_name='rtl')
LTR = CKEditorWidget(config_name='ltr')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_en', 'name_ar', 'slug', 'sort_order')
    list_editable = ('sort_order',)
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'category', 'author', 'is_published', 'published_at', 'views_count')
    list_filter = ('is_published', 'category')
    list_editable = ('is_published',)
    search_fields = ('title_fa', 'title_en', 'title_ar', 'content_fa')
    prepopulated_fields = {'slug': ('title_en',)}
    date_hierarchy = 'published_at'
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('slug', 'category', 'author', 'image', 'is_published')
        }),
        ('فارسی', {
            'fields': ('title_fa', 'summary_fa', 'content_fa')
        }),
        ('English', {
            'fields': ('title_en', 'summary_en', 'content_en')
        }),
        ('العربية', {
            'fields': ('title_ar', 'summary_ar', 'content_ar')
        }),
        ('SEO', {
            'fields': (
                'meta_title_fa', 'meta_title_en', 'meta_title_ar',
                'meta_description_fa', 'meta_description_en', 'meta_description_ar',
            ),
            'classes': ('collapse',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['summary_fa'].widget = RTL
        form.base_fields['summary_en'].widget = LTR
        form.base_fields['summary_ar'].widget = RTL
        return form


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'post', 'language', 'is_approved', 'created_at')
    list_filter   = ('is_approved', 'language')
    list_editable = ('is_approved',)
    search_fields = ('name', 'email', 'body')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('اطلاعات نظر', {
            'fields': ('post', 'name', 'email', 'language', 'body'),
        }),
        ('وضعیت', {
            'fields': ('is_approved', 'created_at'),
        }),
    )
