from django import forms

from .antispam import PHONE_ERRORS, persian_phone_ok
from .captcha import matches as captcha_matches

CAPTCHA_ERRORS = {
    'fa': 'کد تصویر درست نیست یا منقضی شده. کد جدید را وارد کنید.',
    'en': 'The code in the image is wrong or expired. Enter the new code.',
    'ar': 'الرمز في الصورة غير صحيح أو منتهٍ. أدخل الرمز الجديد.',
}

APPT_PHONE_ERRORS = {
    'fa': 'برای گرفتن وقت، شماره تماس را وارد کنید.',
    'en': 'Enter a phone number so we can arrange the appointment.',
    'ar': 'أدخل رقم الهاتف لنتمكن من تنسيق الموعد.',
}


class ContactMessageForm(forms.Form):
    name    = forms.CharField(max_length=120)
    phone   = forms.CharField(max_length=20, required=False)
    email   = forms.EmailField(required=False)
    subject = forms.CharField(max_length=200, required=False)
    message = forms.CharField(widget=forms.Textarea)
    # فیلد تله (honeypot) — کاربر واقعی آن را نمی‌بیند و خالی می‌گذارد؛
    # ربات‌های اسپم آن را پر می‌کنند و درخواست رد می‌شود.
    website = forms.CharField(required=False)
    captcha = forms.CharField(max_length=12)
    wants_appointment = forms.BooleanField(required=False)

    def __init__(self, *args, language='fa', captcha_session=None, **kwargs):
        self.language = language if language in CAPTCHA_ERRORS else 'fa'
        self.captcha_session = captcha_session
        super().__init__(*args, **kwargs)
        self.fields['captcha'].error_messages['required'] = CAPTCHA_ERRORS[self.language]

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('اسپم شناسایی شد.')
        return ''

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        # فقط فرم فارسی؛ بیمار انگلیسی و عربی ممکن است شمارهٔ بین‌المللی بدهد.
        if self.language == 'fa' and phone and not persian_phone_ok(phone):
            raise forms.ValidationError(PHONE_ERRORS['fa'])
        return phone

    def clean(self):
        cleaned = super().clean()
        # کد یک‌بارمصرف است؛ حتی اگر بقیه فیلدها خطا داشته باشند سوزانده می‌شود.
        ok = (
            self.captcha_session is not None
            and captcha_matches(self.captcha_session, cleaned.get('captcha', ''))
        )
        if not ok and 'captcha' not in self.errors:
            self.add_error('captcha', CAPTCHA_ERRORS[self.language])
        if cleaned.get('wants_appointment') and not (cleaned.get('phone') or '').strip():
            if 'phone' not in self.errors:
                self.add_error('phone', APPT_PHONE_ERRORS[self.language])
        return cleaned
