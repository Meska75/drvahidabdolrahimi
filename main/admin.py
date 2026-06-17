from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from .models import (
    ContactMessage, SiteSetting, SiteBanner,
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
    list_display = ('key', 'group_name', 'label_fa', 'type', 'is_editable')
    list_filter = ('group_name', 'type')
    search_fields = ('key', 'label_fa')
    ordering = ('group_name', 'key')


@admin.register(SiteBanner)
class SiteBannerAdmin(admin.ModelAdmin):
    list_display = ('location', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('location', 'is_active')


@admin.register(DoctorEducation)
class DoctorEducationAdmin(admin.ModelAdmin):
    list_display = ('degree_fa', 'institution_fa', 'year', 'sort_order')
    list_editable = ('sort_order',)


@admin.register(DoctorAchievement)
class DoctorAchievementAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'year', 'sort_order')
    list_editable = ('sort_order',)


@admin.register(DoctorClinic)
class DoctorClinicAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'city_fa', 'phone_1', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name_fa', 'phone_1', 'phone_2')


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
