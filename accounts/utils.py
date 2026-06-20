from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import EmailVerificationToken


def send_verification_email(user, request, resend=False):
    """ارسال ایمیل تأیید برای کاربر جدید"""

    # حذف توکن قدیمی و ساخت توکن جدید
    EmailVerificationToken.objects.filter(user=user).delete()
    token_obj = EmailVerificationToken.objects.create(user=user)

    verification_url = request.build_absolute_uri(
        f'/accounts/verify-email/{token_obj.token}/'
    )

    html_message = render_to_string('emails/verification_email.html', {
        'user': user,
        'verification_url': verification_url,
        'resend': resend,
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject='تأیید ایمیل — پنل مدیریت دکتر عبدالرحیمی',
        message=plain_message,
        from_email=None,  # از DEFAULT_FROM_EMAIL در settings استفاده می‌کند
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
