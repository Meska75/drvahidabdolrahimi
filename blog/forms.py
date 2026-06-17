from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
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
