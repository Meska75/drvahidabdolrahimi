from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'پروفایل کاربری'
    verbose_name_plural = 'پروفایل کاربری'
    fieldsets = (
        ('نقش و موبایل', {
            'fields': ('role', 'phone'),
        }),
        ('بیوگرافی', {
            'fields': ('bio_fa', 'bio_en', 'bio_ar', 'avatar'),
            'classes': ('collapse',),
        }),
    )


class CustomUserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_phone', 'is_staff')
    list_select_related = ('profile',)

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except UserProfile.DoesNotExist:
            return '—'
    get_role.short_description = 'نقش'

    def get_phone(self, obj):
        try:
            return obj.profile.phone or '—'
        except UserProfile.DoesNotExist:
            return '—'
    get_phone.short_description = 'موبایل'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    list_editable = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')
    fieldsets = (
        ('کاربر و نقش', {
            'fields': ('user', 'role', 'phone'),
        }),
        ('بیوگرافی', {
            'fields': ('bio_fa', 'bio_en', 'bio_ar', 'avatar'),
            'classes': ('collapse',),
        }),
    )
