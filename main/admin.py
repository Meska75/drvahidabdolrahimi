from django.contrib import admin
from django.utils.html import format_html
from ckeditor.widgets import CKEditorWidget
from .models import (
    ContactMessage, SiteSetting, SiteBanner, SocialLinks,
    DoctorEducation, DoctorAchievement, DoctorClinic,
    FaqItem, PatientTestimonial,
)

RTL = CKEditorWidget(config_name='rtl')
LTR = CKEditorWidget(config_name='ltr')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'language', 'is_read', 'is_replied', 'created_at')
    list_filter = ('is_read', 'is_replied', 'language')
    list_editable = ('is_read', 'is_replied')
    search_fields = ('full_name', 'phone', 'email', 'subject')
    readonly_fields = ('created_at',)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('label_fa', 'fa_val', 'en_val', 'ar_val', 'group_name')
    list_filter = ('group_name',)
    search_fields = ('label_fa', 'key')
    ordering = ('group_name', 'key')
    fieldsets = (
        (None, {
            'description': '⚡ مقادیر زیر در صفحه اصلی و صفحه «درباره» نمایش داده می‌شوند. فقط بخش «مقادیر» را ویرایش کنید.',
            'fields': ('label_fa',),
        }),
        ('مقادیر نمایشی', {
            'fields': ('value_fa', 'value_en', 'value_ar'),
        }),
        ('تنظیمات پیشرفته', {
            'classes': ('collapse',),
            'fields': ('key', 'group_name', 'type', 'is_editable'),
        }),
    )

    @admin.display(description='فارسی')
    def fa_val(self, obj):
        return obj.value_fa or '—'

    @admin.display(description='انگلیسی')
    def en_val(self, obj):
        return obj.value_en or '—'

    @admin.display(description='عربی')
    def ar_val(self, obj):
        return obj.value_ar or '—'


@admin.register(SiteBanner)
class SiteBannerAdmin(admin.ModelAdmin):
    list_display = ('preview', 'location', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('location', 'is_active')

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:90px;height:50px;object-fit:cover;'
                'border-radius:6px;border:1px solid #475569;display:block;">',
                obj.image.url
            )
        return format_html('<span style="color:#64748b;font-size:0.8rem;">—</span>')


@admin.register(DoctorEducation)
class DoctorEducationAdmin(admin.ModelAdmin):
    list_display = ('degree_fa', 'institution_fa', 'year', 'sort_order')
    list_editable = ('sort_order',)


@admin.register(DoctorAchievement)
class DoctorAchievementAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'year', 'sort_order')
    list_editable = ('sort_order',)


@admin.register(SocialLinks)
class SocialLinksAdmin(admin.ModelAdmin):
    """فقط یک رکورد — مستقیم به فرم ویرایش برود"""

    def has_add_permission(self, request):
        return not SocialLinks.objects.exists()

    def changelist_view(self, request, extra_context=None):
        obj, _ = SocialLinks.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        return redirect(f'/admin/main/sociallinks/{obj.pk}/change/')

    fieldsets = (
        ('شبکه‌های اجتماعی', {
            'description': '⚡ پر کردن هر فیلد، آیکون آن شبکه را در هدر و فوتر سایت نمایش می‌دهد. خالی گذاشتن = پنهان.',
            'fields': ('instagram', 'telegram', 'whatsapp', 'youtube', 'aparat', 'linkedin'),
        }),
    )


@admin.register(DoctorClinic)
class DoctorClinicAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'city_fa', 'phone_1', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name_fa', 'phone_1', 'phone_2')
    fieldsets = (
        ('⭐ اطلاعات اصلی — هدر و فوتر سایت', {
            'description': '🔔 اولین مطب فعال (کمترین ترتیب نمایش) به عنوان شماره تماس و آدرس در هدر و فوتر همه صفحات نمایش داده می‌شود.',
            'fields': ('name_fa', 'name_en', 'name_ar', 'is_active', 'sort_order'),
        }),
        ('تلفن‌ها', {
            'fields': ('phone_1', 'phone_2'),
        }),
        ('آدرس', {
            'fields': ('address_fa', 'address_en', 'address_ar', 'city_fa', 'city_en', 'city_ar'),
        }),
        ('ساعت کاری', {
            'fields': ('schedule_fa', 'schedule_en', 'schedule_ar'),
        }),
        ('تصویر و نقشه', {
            'fields': ('image', 'map_url'),
        }),
    )


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    list_filter = ('category', 'is_active')
    fieldsets = (
        ('فارسی', {'fields': ('question_fa', 'answer_fa')}),
        ('English', {'fields': ('question_en', 'answer_en'), 'classes': ('collapse',)}),
        ('العربية', {'fields': ('question_ar', 'answer_ar'), 'classes': ('collapse',)}),
        ('تنظیمات', {'fields': ('category', 'is_active', 'sort_order')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['answer_fa'].widget = RTL
        form.base_fields['answer_en'].widget = LTR
        form.base_fields['answer_ar'].widget = RTL
        return form


@admin.register(PatientTestimonial)
class PatientTestimonialAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    list_editable = ('is_approved',)
    search_fields = ('name_fa', 'content_fa')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('فارسی', {'fields': ('name_fa', 'content_fa')}),
        ('English', {'fields': ('name_en', 'content_en'), 'classes': ('collapse',)}),
        ('العربية', {'fields': ('name_ar', 'content_ar'), 'classes': ('collapse',)}),
        ('تأیید', {'fields': ('rating', 'is_approved', 'approved_by', 'approved_at', 'sort_order')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['content_fa'].widget = RTL
        form.base_fields['content_en'].widget = LTR
        form.base_fields['content_ar'].widget = RTL
        return form
