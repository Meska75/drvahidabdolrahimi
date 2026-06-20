from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, EmailVerificationToken
from .forms import AdminUserCreationForm, AdminUserChangeForm
from .utils import send_verification_email


# ===== رنگ و آیکون هر نقش =====
ROLE_BADGE = {
    'superadmin': ('<span style="background:#7c3aed;color:#fff;padding:2px 10px;'
                   'border-radius:20px;font-size:0.78rem;font-weight:700;">مدیر ارشد</span>'),
    'editor':     ('<span style="background:#0891b2;color:#fff;padding:2px 10px;'
                   'border-radius:20px;font-size:0.78rem;font-weight:700;">ویرایشگر</span>'),
    'author':     ('<span style="background:#16a34a;color:#fff;padding:2px 10px;'
                   'border-radius:20px;font-size:0.78rem;font-weight:700;">نویسنده</span>'),
    'viewer':     ('<span style="background:#64748b;color:#fff;padding:2px 10px;'
                   'border-radius:20px;font-size:0.78rem;font-weight:700;">بازدیدکننده</span>'),
}


class CustomUserAdmin(DjangoUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm

    # ===== لیست کاربران =====
    list_display = ('username', 'email', 'get_phone', 'get_role_badge', 'get_status_badge', 'get_verified_badge')
    list_filter = ('is_active', 'profile__role')
    search_fields = ('username', 'email', 'profile__phone')
    ordering = ('-date_joined',)
    list_select_related = ('profile',)
    list_per_page = 20

    # ===== فرم ساخت کاربر جدید (ساده‌شده) =====
    add_fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('username', 'email', 'phone'),
            'classes': ('wide',),
        }),
        ('نقش و دسترسی', {
            'fields': ('role', 'is_active'),
            'classes': ('wide',),
        }),
        ('رمز عبور', {
            'fields': ('password1', 'password2'),
            'classes': ('wide',),
            'description': 'رمز عبور باید حداقل ۸ کاراکتر و ترکیب حروف و اعداد باشد.',
        }),
    )

    # ===== فرم ویرایش کاربر موجود =====
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('username', 'email', 'phone'),
        }),
        ('نقش و دسترسی', {
            'fields': ('role', 'is_active'),
        }),
        ('تغییر رمز عبور', {
            'fields': ('password',),
            'classes': ('collapse',),
            'description': 'برای تغییر رمز عبور از لینک زیر استفاده کنید.',
        }),
    )

    # ===== ستون‌های سفارشی =====
    def get_phone(self, obj):
        try:
            return obj.profile.phone or '—'
        except UserProfile.DoesNotExist:
            return '—'
    get_phone.short_description = 'شماره تماس'

    def get_role_badge(self, obj):
        try:
            role = obj.profile.role
            return format_html(ROLE_BADGE.get(role, role))
        except UserProfile.DoesNotExist:
            return '—'
    get_role_badge.short_description = 'نقش'

    def get_status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#dcfce7;color:#15803d;padding:2px 10px;'
                'border-radius:20px;font-size:0.78rem;font-weight:700;">● فعال</span>'
            )
        return format_html(
            '<span style="background:#fee2e2;color:#dc2626;padding:2px 10px;'
            'border-radius:20px;font-size:0.78rem;font-weight:700;">○ غیرفعال</span>'
        )
    get_status_badge.short_description = 'وضعیت'

    def get_verified_badge(self, obj):
        has_token = EmailVerificationToken.objects.filter(user=obj).exists()
        if not has_token and obj.is_active:
            return format_html(
                '<span style="background:#e0f2fe;color:#0369a1;padding:2px 10px;'
                'border-radius:20px;font-size:0.78rem;">✓ تأیید شده</span>'
            )
        if has_token:
            return format_html(
                '<span style="background:#fef3c7;color:#b45309;padding:2px 10px;'
                'border-radius:20px;font-size:0.78rem;">⏳ در انتظار تأیید</span>'
            )
        return '—'
    get_verified_badge.short_description = 'ایمیل'

    # ===== ذخیره کاربر جدید =====
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # ذخیره پروفایل (phone و role)
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        profile.phone = form.cleaned_data.get('phone', '') or ''
        profile.role = form.cleaned_data.get('role', 'viewer')
        profile.save()

        # ارسال ایمیل تأیید فقط برای کاربر جدید با ایمیل
        if not change and obj.email:
            try:
                send_verification_email(obj, request)
                messages.success(
                    request,
                    f'ایمیل تأیید به {obj.email} ارسال شد. کاربر پس از کلیک روی لینک فعال می‌شود.'
                )
            except Exception as e:
                messages.warning(
                    request,
                    f'کاربر ساخته شد ولی ارسال ایمیل تأیید ناموفق بود: {e}'
                )

    # ===== اکشن ارسال مجدد ایمیل تأیید =====
    def resend_verification(self, request, queryset):
        sent = 0
        for user in queryset:
            if user.email:
                try:
                    send_verification_email(user, request, resend=True)
                    sent += 1
                except Exception:
                    pass
        self.message_user(request, f'ایمیل تأیید برای {sent} کاربر ارسال شد.')
    resend_verification.short_description = 'ارسال مجدد ایمیل تأیید'

    actions = ['resend_verification']


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
