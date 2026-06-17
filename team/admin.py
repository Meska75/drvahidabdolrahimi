from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from .models import TeamMember

RTL = CKEditorWidget(config_name='rtl')
LTR = CKEditorWidget(config_name='ltr')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'title_fa', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name_fa', 'name_en', 'title_fa')
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('photo', 'is_active', 'sort_order'),
        }),
        ('فارسی', {
            'fields': ('name_fa', 'title_fa', 'bio_fa'),
        }),
        ('English', {
            'fields': ('name_en', 'title_en', 'bio_en'),
            'classes': ('collapse',),
        }),
        ('العربية', {
            'fields': ('name_ar', 'title_ar', 'bio_ar'),
            'classes': ('collapse',),
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('instagram_url', 'telegram_url', 'whatsapp_number', 'linkedin_url'),
            'classes': ('collapse',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['bio_fa'].widget = RTL
        form.base_fields['bio_en'].widget = LTR
        form.base_fields['bio_ar'].widget = RTL
        return form
