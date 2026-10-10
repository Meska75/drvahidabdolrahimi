from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# کلیدهایی که قبل از خواندن فایل‌ها در محیط سیستم بودند — هیچ‌وقت بازنویسی نمی‌شوند
_PREEXISTING_ENV = set(os.environ)


def _load_dotenv(path: Path, *, override: bool = False) -> None:
    """خواندن فایل .env بدون وابستگی اضافه.

    override=False: اگر کلید از قبل در محیط باشد، دست نمی‌خورد.
    override=True: روی مقادیر آمده از فایل‌های قبلی می‌نویسد، اما متغیرهای
    واقعی سیستم‌عامل (قبل از لود) را بازنویسی نمی‌کند.
    """
    if not path.is_file():
        return
    try:
        raw = path.read_text(encoding='utf-8')
    except OSError:
        return
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        if not key:
            continue
        if key in os.environ:
            if not override or key in _PREEXISTING_ENV:
                continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        os.environ[key] = value


_load_dotenv(BASE_DIR / '.env')
# تنظیمات لوکال روی .env پروداکشن می‌نشیند (مثلاً DEBUG=True) — در گیت نیست
_load_dotenv(BASE_DIR / '.env.local', override=True)

# ===== کلیدها و حالت اجرا — از محیط خوانده می‌شوند =====
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-&l8!^zsr=hc5t07uhmyi)4@=9s=j@@%&v%sw7^&l578ura36uc'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]

# ===== پذیرش۲۴ — رزرو نوبت آنلاین =====
PAZIRESH24_API_KEY  = os.environ.get('PAZIRESH24_API_KEY', '')
PAZIRESH24_DOCTOR_ID = os.environ.get('PAZIRESH24_DOCTOR_ID', '')
PAZIRESH24_BASE_URL  = os.environ.get('PAZIRESH24_BASE_URL', 'https://api.paziresh24.com')

# ===== اپ‌های نصب‌شده =====
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'imagekit',
    'django_cleanup.apps.CleanupConfig',
    'ckeditor',
    'ckeditor_uploader',
    'main',
    'siteimages',
    'services',
    'blog',
    'accounts',
    'team',
    'gallery',
    'videos',
    'chatbot.apps.ChatbotConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.site_context',
                'chatbot.context_processors.chatbot_widget',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ===== دیتابیس =====
# اگر DB_NAME در محیط باشد، PostgreSQL همان سرور استفاده می‌شود.
# روی این کامپیوتر .env.local نام دیتابیس را خالی می‌گذارد تا تست‌ها با SQLite اجرا شوند.
_db_name = os.environ.get('DB_NAME', '').strip()
if _db_name:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _db_name,
            'USER': os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 60,
            'CONN_HEALTH_CHECKS': True,
            'OPTIONS': {
                'connect_timeout': 10,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ===== اعتبارسنجی رمز عبور =====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===== زبان و منطقه زمانی =====
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# ===== فایل‌های استاتیک =====
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# روی لوکال می‌توان MEDIA_URL را به دامنه پروداکشن داد تا تصاویر آپلودی دیده شوند
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'static_files',
]

# سقف آپلود — پیش‌فرض Django فقط ۲.۵ MB است و قبل از فشرده‌سازی ImageKit درخواست را رد می‌کند
# تصاویر تا ۱۰ MB و ویدیو تا ۵۰ MB در مدل‌ها مجازند؛ اینجا کمی بالاتر می‌گذاریم
DATA_UPLOAD_MAX_MEMORY_SIZE = 55 * 1024 * 1024   # ۵۵ MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 55 * 1024 * 1024   # ۵۵ MB


# whitenoise — فشرده‌سازی و cache فایل‌های استاتیک در production
# در development از storage پیش‌فرض Django استفاده می‌شود
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== چت‌بات =====
CHATBOT_MEMORY_DAYS = 7

# ===== تنظیمات CKEditor =====
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = 'pillow'

CKEDITOR_CONFIGS = {
    # ویرایشگر راست‌چین (فارسی / عربی)
    'rtl': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format', 'FontSize'],
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['BidiLtr', 'BidiRtl'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'HorizontalRule'],
            ['RemoveFormat', 'Source'],
        ],
        'height': 450,
        'width': '100%',
        'language': 'fa',
        'contentsLangDirection': 'rtl',
        'extraPlugins': 'bidi',
    },
    # ویرایشگر چپ‌چین (انگلیسی)
    'ltr': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format', 'FontSize'],
            ['Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['BidiLtr', 'BidiRtl'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'HorizontalRule'],
            ['RemoveFormat', 'Source'],
        ],
        'height': 450,
        'width': '100%',
        'language': 'en',
        'contentsLangDirection': 'ltr',
        'extraPlugins': 'bidi',
    },
}

# ===== احراز هویت چندروشه =====
AUTHENTICATION_BACKENDS = [
    'accounts.backends.FlexibleAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ===== تنظیمات Jazzmin (پنل ادمین حرفه‌ای) =====
JAZZMIN_SETTINGS = {
    "site_title": "پنل مدیریت",
    "site_header": "دکتر عبدالرحیمی",
    "site_brand": "دکتر عبدالرحیمی",
    "site_logo": "images/logo/logo.png",
    "login_logo": "images/logo/logo.png",
    "site_icon": "images/logo/favicon.png",
    "welcome_sign": "خوش آمدید — می‌توانید با یوزرنیم، ایمیل یا شماره موبایل وارد شوید",
    "copyright": "دکتر وحید عبدالرحیمی",
    "search_model": ["blog.Post", "main.ContactMessage", "gallery.GalleryImage"],
    "user_avatar": None,

    "topmenu_links": [
        {"name": "مشاهده سایت", "url": "/", "new_window": True, "icon": "fas fa-external-link-alt"},
        {"name": "پیام‌های تماس", "url": "/admin/main/contactmessage/", "icon": "fas fa-envelope"},
        {"name": "درخواست نوبت", "url": "/admin/main/appointmentrequest/", "icon": "fas fa-calendar-check"},
        {"model": "auth.User"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    "order_with_respect_to": [
        "chatbot", "main", "siteimages", "blog", "gallery", "videos", "team", "services", "accounts", "auth",
    ],

    "custom_links": {
        "blog": [{
            "name": "نوشتن مقاله جدید",
            "url": "/admin/blog/post/add/",
            "icon": "fas fa-plus-circle",
            "permissions": ["blog.add_post"],
        }],
        "gallery": [{
            "name": "افزودن تصویر",
            "url": "/admin/gallery/galleryimage/add/",
            "icon": "fas fa-plus-circle",
            "permissions": ["gallery.add_galleryimage"],
        }],
        "videos": [{
            "name": "افزودن ویدیو",
            "url": "/admin/videos/sitevideo/add/",
            "icon": "fas fa-plus-circle",
            "permissions": ["videos.add_sitevideo"],
        }],
        "siteimages": [{
            "name": "افزودن بنر",
            "url": "/admin/siteimages/sitebannerproxy/add/",
            "icon": "fas fa-plus-circle",
            "permissions": ["main.add_sitebanner"],
        }],
        "chatbot": [{
            "name": "پروفایل و پرامپت",
            "url": "/admin/chatbot/chatbotprofile/",
            "icon": "fas fa-sliders-h",
            "permissions": ["chatbot.change_chatbotprofile"],
        }],
    },

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "main.ContactMessage": "fas fa-envelope",
        "main.AppointmentRequest": "fas fa-calendar-check",
        "main.FaqItem": "fas fa-question-circle",
        "main.PatientTestimonial": "fas fa-star",
        "main.SiteSetting": "fas fa-cog",
        "main.SocialLinks": "fas fa-share-alt",
        "main.DoctorEducation": "fas fa-graduation-cap",
        "main.DoctorAchievement": "fas fa-award",
        "main.DoctorClinic": "fas fa-hospital",
        "siteimages": "fas fa-photo-video",
        "siteimages.SiteBannerProxy": "fas fa-image",
        "siteimages.DoctorPhoto": "fas fa-user-circle",
        "siteimages.BuildingPhoto": "fas fa-building",
        "siteimages.ClinicInteriorPhoto": "fas fa-clinic-medical",
        "blog.Post": "fas fa-newspaper",
        "blog.Category": "fas fa-tags",
        "blog.Comment": "fas fa-comments",
        "gallery.GalleryImage": "fas fa-images",
        "gallery.GalleryTag": "fas fa-tag",
        "team.TeamMember": "fas fa-user-md",
        "videos.SiteVideo": "fas fa-video",
        "videos.VideoCategory": "fas fa-film",
        "services.ServiceCategory": "fas fa-list",
        "services.ServiceItem": "fas fa-stethoscope",
        "accounts.UserProfile": "fas fa-id-card",
        "chatbot": "fas fa-robot",
        "chatbot.ChatbotProfile": "fas fa-user-md",
        "chatbot.LlmConnection": "fas fa-plug",
        "chatbot.EmbeddingConnection": "fas fa-project-diagram",
        "chatbot.KnowledgeFile": "fas fa-file-alt",
        "chatbot.Conversation": "fas fa-comments",
    },

    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_jazzmin.js",
    "use_google_fonts_cdn": False,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-info",
    "accent": "accent-teal",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-teal",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "default_theme_mode": "light",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}

# ===== تنظیمات ایمیل (Gmail SMTP) =====
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    f'پنل مدیریت دکتر عبدالرحیمی <{os.environ.get("EMAIL_HOST_USER", "")}>'
)
SERVER_EMAIL = EMAIL_HOST_USER

# ===== تنظیمات امنیتی پروداکشن =====
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # ریدایرکت HTTP به HTTPS — چون پشت nginx (reverse proxy) هستیم
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # دامنه‌های مجاز برای CSRF
    CSRF_TRUSTED_ORIGINS = [
        'https://drabdolrahimi.ir',
        'https://www.drabdolrahimi.ir',
        'https://drabdolrahimi.com',
        'https://www.drabdolrahimi.com',
    ]
