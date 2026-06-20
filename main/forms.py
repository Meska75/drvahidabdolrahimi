from django import forms


class ContactMessageForm(forms.Form):
    name    = forms.CharField(max_length=120)
    phone   = forms.CharField(max_length=20, required=False)
    email   = forms.EmailField(required=False)
    subject = forms.CharField(max_length=200, required=False)
    message = forms.CharField(widget=forms.Textarea)
