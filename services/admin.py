from django import forms
from django.contrib import admin
from .models import ServiceItem


class ServiceItemForm(forms.ModelForm):
    """فرم سفارشی برای نمایش textarea با محدودیت کاراکتر"""

    class Meta:
        model = ServiceItem
        fields = '__all__'
        widgets = {
            # متن خلاصه — صفحه اصلی (max 90)
            'summary_fa': forms.Textarea(attrs={
                'rows': 3, 'maxlength': 90,
                'style': 'resize:vertical; direction:rtl;',
                'placeholder': 'حداکثر ۹۰ کاراکتر — نمایش در کارت صفحه اصلی',
            }),
            'summary_en': forms.Textarea(attrs={
                'rows': 3, 'maxlength': 90,
                'style': 'resize:vertical;',
                'placeholder': 'Max 90 chars — shown on home page card',
            }),
            'summary_ar': forms.Textarea(attrs={
                'rows': 3, 'maxlength': 90,
                'style': 'resize:vertical; direction:rtl;',
                'placeholder': 'الحد الأقصى ٩٠ حرفًا',
            }),
            # توضیح کوتاه — صفحه خدمات (max 250)
            'description_fa': forms.Textarea(attrs={
                'rows': 5, 'maxlength': 250,
                'style': 'resize:vertical; direction:rtl;',
                'placeholder': 'حداکثر ۲۵۰ کاراکتر — نمایش در صفحه خدمات',
            }),
            'description_en': forms.Textarea(attrs={
                'rows': 5, 'maxlength': 250,
                'style': 'resize:vertical;',
                'placeholder': 'Max 250 chars — shown on services page',
            }),
            'description_ar': forms.Textarea(attrs={
                'rows': 5, 'maxlength': 250,
                'style': 'resize:vertical; direction:rtl;',
                'placeholder': 'الحد الأقصى ٢٥٠ حرفًا',
            }),
        }


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    form = ServiceItemForm
    list_display = ('title_fa', 'type', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    list_filter = ('type', 'is_active')
    search_fields = ('title_fa', 'title_en')
    fieldsets = (
        ('تنظیمات', {
            'description': '🔵 نوع خدمت تعیین می‌کند در کدام صفحه نمایش داده شود.',
            'fields': ('type', 'image', 'is_active', 'sort_order'),
        }),
        ('فارسی', {
            'description': 'متن خلاصه در کارت صفحه اصلی — توضیح کوتاه در صفحه خدمات نمایش داده می‌شود.',
            'fields': ('title_fa', 'summary_fa', 'description_fa'),
        }),
        ('English', {
            'classes': ('collapse',),
            'fields': ('title_en', 'summary_en', 'description_en'),
        }),
        ('العربية', {
            'classes': ('collapse',),
            'fields': ('title_ar', 'summary_ar', 'description_ar'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': (
                'meta_title_fa', 'meta_title_en', 'meta_title_ar',
                'meta_description_fa', 'meta_description_en', 'meta_description_ar',
            ),
        }),
    )
