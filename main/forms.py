from django import forms


class ContactMessageForm(forms.Form):
    name    = forms.CharField(max_length=120)
    phone   = forms.CharField(max_length=20, required=False)
    email   = forms.EmailField(required=False)
    subject = forms.CharField(max_length=200, required=False)
    message = forms.CharField(widget=forms.Textarea)
    # فیلد تله (honeypot) — کاربر واقعی آن را نمی‌بیند و خالی می‌گذارد؛
    # ربات‌های اسپم آن را پر می‌کنند و درخواست رد می‌شود.
    website = forms.CharField(required=False)

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('اسپم شناسایی شد.')
        return ''
