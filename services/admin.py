from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from .models import ServiceCategory, ServiceItem

RTL = CKEditorWidget(config_name='rtl')
LTR = CKEditorWidget(config_name='ltr')


class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 1
    fields = ('title_fa', 'icon_class', 'is_active', 'sort_order')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'type', 'slug')
    list_filter = ('type',)
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [ServiceItemInline]


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'category', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    list_filter = ('category', 'is_active')
    search_fields = ('title_fa', 'title_en')
    fieldsets = (
        ('فارسی', {'fields': ('title_fa', 'description_fa')}),
        ('English', {'fields': ('title_en', 'description_en'), 'classes': ('collapse',)}),
        ('العربية', {'fields': ('title_ar', 'description_ar'), 'classes': ('collapse',)}),
        ('SEO', {'fields': ('meta_title_fa', 'meta_title_en', 'meta_title_ar',
                             'meta_description_fa', 'meta_description_en', 'meta_description_ar'),
                 'classes': ('collapse',)}),
        ('تنظیمات', {'fields': ('category', 'icon_class', 'image', 'is_active', 'sort_order')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['description_fa'].widget = RTL
        form.base_fields['description_en'].widget = LTR
        form.base_fields['description_ar'].widget = RTL
        return form
