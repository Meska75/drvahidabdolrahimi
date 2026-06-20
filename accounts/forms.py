from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

# توضیح هر نقش برای نمایش در فرم
ROLE_HELP = {
    'superadmin': 'دسترسی کامل به همه بخش‌ها — معادل superuser',
    'editor':     'مدیریت بلاگ، گالری، ویدیو، تیم، خدمات — بدون دسترسی به تنظیمات حیاتی',
    'author':     'فقط نوشتن و ویرایش مقالات و محتوای خود — بدون حذف یا مدیریت دیگران',
    'viewer':     'فقط مشاهده محتوا — بدون هیچ‌گونه تغییر',
}

ROLE_CHOICES_WITH_EMPTY = [('', '--- انتخاب نقش ---')] + UserProfile.ROLE_CHOICES


class AdminUserCreationForm(UserCreationForm):
    """فرم ساده‌شده ساخت کاربر در پنل ادمین"""

    email = forms.EmailField(
        required=True,
        label='ایمیل (Gmail)',
        widget=forms.EmailInput(attrs={'placeholder': 'example@gmail.com', 'dir': 'ltr'}),
        help_text='یک ایمیل تأیید به این آدرس ارسال می‌شود — کاربر پس از کلیک روی لینک فعال می‌شود.',
    )
    phone = forms.CharField(
        required=False,
        max_length=20,
        label='شماره تماس',
        widget=forms.TextInput(attrs={'placeholder': '09xxxxxxxxx', 'dir': 'ltr'}),
        help_text='برای ورود با شماره موبایل — فرمت: 09013434195',
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES_WITH_EMPTY,
        required=True,
        label='نقش کاربر',
    )
    is_active = forms.BooleanField(
        required=False,
        initial=False,
        label='کاربر فعال است',
        help_text='اگر تیک نزنید، کاربر در دیتابیس ذخیره می‌شود ولی نمی‌تواند وارد شود. '
                  'پس از تأیید ایمیل، به‌صورت خودکار فعال می‌شود.',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone', 'role', 'password1', 'password2', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # راهنمای نقش‌ها
        role_lines = '\n'.join(
            f'• {label}: {ROLE_HELP[val]}' for val, label in UserProfile.ROLE_CHOICES
        )
        self.fields['role'].help_text = role_lines
        self.fields['username'].help_text = 'فقط حروف انگلیسی، اعداد و نمادهای @/./+/-/_ مجاز است.'
        self.fields['password1'].help_text = 'حداقل ۸ کاراکتر، ترکیب حروف و اعداد.'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone and UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError('این شماره تماس قبلاً ثبت شده است.')
        return phone


class AdminUserChangeForm(UserChangeForm):
    """فرم ویرایش کاربر در پنل ادمین"""

    password = None  # فیلد رمز پیش‌فرض Django را پنهان می‌کند

    phone = forms.CharField(
        required=False,
        max_length=20,
        label='شماره تماس',
        widget=forms.TextInput(attrs={'placeholder': '09xxxxxxxxx', 'dir': 'ltr'}),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES_WITH_EMPTY,
        required=True,
        label='نقش کاربر',
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'phone', 'role', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # مقدار اولیه phone و role از پروفایل
        if self.instance and self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields['phone'].initial = profile.phone
                self.fields['role'].initial = profile.role
            except UserProfile.DoesNotExist:
                pass
        role_lines = '\n'.join(
            f'• {label}: {ROLE_HELP[val]}' for val, label in UserProfile.ROLE_CHOICES
        )
        self.fields['role'].help_text = role_lines

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            qs = UserProfile.objects.filter(phone=phone)
            if self.instance and self.instance.pk:
                qs = qs.exclude(user=self.instance)
            if qs.exists():
                raise forms.ValidationError('این شماره تماس قبلاً ثبت شده است.')
        return phone
