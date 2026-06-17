from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class FlexibleAuthBackend(ModelBackend):
    """ورود با یوزرنیم، ایمیل یا شماره موبایل"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # جستجو با یوزرنیم یا ایمیل
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            user = None
        except User.MultipleObjectsReturned:
            user = User.objects.filter(email=username).order_by('id').first()

        # اگر پیدا نشد، با شماره موبایل جستجو کن
        if user is None:
            try:
                from accounts.models import UserProfile
                profile = UserProfile.objects.select_related('user').get(phone=username)
                user = profile.user
            except UserProfile.DoesNotExist:
                return None

        if user is not None and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
