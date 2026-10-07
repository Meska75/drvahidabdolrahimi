from datetime import timedelta

from django.db.models import F
from django.utils import timezone

from chatbot.models import RateLimitHit


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or '0.0.0.0'


def _window_start(now, kind):
    if kind == 'minute':
        return now.replace(second=0, microsecond=0)
    return now.replace(minute=0, second=0, microsecond=0)


def allow_message(profile, ip):
    now = timezone.now()
    key = f'{profile.pk}:{ip}'
    limits = {
        'minute': profile.rate_limit_per_minute or 10,
        'hour': profile.rate_limit_per_hour or 40,
    }
    for kind, limit in limits.items():
        start = _window_start(now, kind)
        obj, created = RateLimitHit.objects.get_or_create(
            key=key,
            window_type=kind,
            window_start=start,
            defaults={'count': 1},
        )
        if not created:
            RateLimitHit.objects.filter(pk=obj.pk).update(count=F('count') + 1)
            obj.refresh_from_db()
        if obj.count > limit:
            return False
    # پاکسازی سبک رکوردهای کهنه
    cutoff = now - timedelta(days=2)
    RateLimitHit.objects.filter(window_start__lt=cutoff).delete()
    return True
