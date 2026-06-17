import html
from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter(name='clean_html')
def clean_html(value):
    """strip HTML tags and decode HTML entities (e.g. &nbsp; → space)"""
    if not value:
        return ''
    return html.unescape(strip_tags(str(value)))
