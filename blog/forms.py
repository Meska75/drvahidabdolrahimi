from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    # فیلد تله (honeypot) ضد اسپم — کاربر واقعی نمی‌بیند و خالی می‌گذارد
    website = forms.CharField(required=False)

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('اسپم شناسایی شد.')
        return ''

    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'cmt-form-control',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'cmt-form-control',
                'autocomplete': 'email',
            }),
            'body': forms.Textarea(attrs={
                'class': 'cmt-form-control cmt-form-control--textarea',
                'rows': 4,
            }),
        }
