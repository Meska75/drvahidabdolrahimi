import html
from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter(name='clean_html')
def clean_html(value):
    """حذف تگ HTML و تبدیل entityها (مثل &zwnj; و &nbsp;) به کاراکتر واقعی"""
    if not value:
        return ''
    text = strip_tags(str(value))
    # دو بار unescape برای مواردی مثل &amp;zwnj;
    for _ in range(2):
        text = html.unescape(text)
    return text.replace('&zwnj;', '\u200c')
