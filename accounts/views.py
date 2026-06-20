from django.shortcuts import render, get_object_or_404
from .models import EmailVerificationToken


def verify_email(request, token):
    """فعال‌سازی کاربر پس از کلیک روی لینک تأیید ایمیل"""

    token_obj = get_object_or_404(EmailVerificationToken, token=token)

    if token_obj.is_expired():
        return render(request, 'accounts/verify_result.html', {
            'success': False,
            'reason': 'expired',
            'username': token_obj.user.username,
        })

    user = token_obj.user
    user.is_active = True
    user.save(update_fields=['is_active'])

    # توکن یکبار مصرف است — حذف شود
    token_obj.delete()

    return render(request, 'accounts/verify_result.html', {
        'success': True,
        'username': user.username,
    })
