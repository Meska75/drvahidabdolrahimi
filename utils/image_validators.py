from django.core.exceptions import ValidationError


class FileSizeValidator:
    """
    Validator قابل serialize برای محدود کردن حجم فایل آپلودی.
    مثال: validators=[FileSizeValidator(max_mb=5)]
    """
    def __init__(self, max_mb: int):
        self.max_mb = max_mb

    def __call__(self, file):
        limit = self.max_mb * 1024 * 1024
        if file.size > limit:
            raise ValidationError(
                f'حجم فایل ({file.size / (1024*1024):.1f} MB) '
                f'بیشتر از حد مجاز ({self.max_mb} MB) است. '
                f'لطفاً تصویر را فشرده کنید.'
            )

    def __eq__(self, other):
        return isinstance(other, FileSizeValidator) and self.max_mb == other.max_mb

    def deconstruct(self):
        return (
            'utils.image_validators.FileSizeValidator',
            [self.max_mb],
            {},
        )


class VideoSizeValidator:
    """Validator برای فایل ویدیو — با پیشنهاد استفاده از embed"""
    def __init__(self, max_mb: int = 50):
        self.max_mb = max_mb

    def __call__(self, file):
        limit = self.max_mb * 1024 * 1024
        if file.size > limit:
            raise ValidationError(
                f'حجم ویدیو ({file.size / (1024*1024):.0f} MB) '
                f'بیشتر از {self.max_mb} MB است. '
                f'پیشنهاد: ویدیو را در آپارات یا یوتیوب آپلود کنید و از کد embed استفاده نمایید.'
            )

    def __eq__(self, other):
        return isinstance(other, VideoSizeValidator) and self.max_mb == other.max_mb

    def deconstruct(self):
        return (
            'utils.image_validators.VideoSizeValidator',
            [self.max_mb],
            {},
        )


# shortcut برای راحتی استفاده
def validate_image_size(max_mb: int) -> FileSizeValidator:
    return FileSizeValidator(max_mb)


def validate_video_size(max_mb: int = 50) -> VideoSizeValidator:
    return VideoSizeValidator(max_mb)
