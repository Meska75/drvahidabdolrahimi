from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactMessage


class PageLoadTests(TestCase):
    """چک می‌کند همه صفحات اصلی بدون خطا لود می‌شوند."""

    def setUp(self):
        self.client = Client()

    # ---- فارسی ----
    def test_persian_home(self):
        r = self.client.get(reverse('main:persian_home'), HTTP_COOKIE='dr_lang=fa')
        self.assertEqual(r.status_code, 200)

    def test_persian_about(self):
        r = self.client.get(reverse('main:persian_about'))
        self.assertEqual(r.status_code, 200)

    def test_persian_contact(self):
        r = self.client.get(reverse('main:persian_contact'))
        self.assertEqual(r.status_code, 200)

    def test_persian_faq(self):
        r = self.client.get(reverse('main:persian_faq'))
        self.assertEqual(r.status_code, 200)

    def test_persian_search(self):
        r = self.client.get(reverse('main:persian_search'))
        self.assertEqual(r.status_code, 200)

    # ---- انگلیسی ----
    def test_english_home(self):
        r = self.client.get(reverse('english:english_home'))
        self.assertEqual(r.status_code, 200)

    def test_english_about(self):
        r = self.client.get(reverse('english:english_about'))
        self.assertEqual(r.status_code, 200)

    def test_english_contact(self):
        r = self.client.get(reverse('english:english_contact'))
        self.assertEqual(r.status_code, 200)

    def test_english_faq(self):
        r = self.client.get(reverse('english:english_faq'))
        self.assertEqual(r.status_code, 200)

    # ---- عربی ----
    def test_arabic_home(self):
        r = self.client.get(reverse('arabic:arabic_home'))
        self.assertEqual(r.status_code, 200)

    def test_arabic_about(self):
        r = self.client.get(reverse('arabic:arabic_about'))
        self.assertEqual(r.status_code, 200)

    def test_arabic_contact(self):
        r = self.client.get(reverse('arabic:arabic_contact'))
        self.assertEqual(r.status_code, 200)

    def test_arabic_faq(self):
        r = self.client.get(reverse('arabic:arabic_faq'))
        self.assertEqual(r.status_code, 200)


class LanguageRedirectTests(TestCase):
    """وقتی کاربر برای اول بار وارد می‌شود (بدون کوکی)، باید به زبان مرورگرش هدایت شود."""

    def test_arabic_browser_redirects_to_ar(self):
        r = self.client.get('/', HTTP_ACCEPT_LANGUAGE='ar,en;q=0.9')
        self.assertRedirects(r, '/ar/', fetch_redirect_response=False)

    def test_english_browser_redirects_to_en(self):
        r = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9')
        self.assertRedirects(r, '/en/', fetch_redirect_response=False)

    def test_persian_browser_stays_on_home(self):
        r = self.client.get('/', HTTP_ACCEPT_LANGUAGE='fa,en;q=0.5')
        self.assertEqual(r.status_code, 200)

    def test_with_cookie_no_redirect(self):
        # کاربری که قبلاً فارسی انتخاب کرده، حتی با مرورگر عربی ریدایرکت نمی‌شود
        r = self.client.get('/', HTTP_ACCEPT_LANGUAGE='ar', HTTP_COOKIE='dr_lang=fa')
        self.assertEqual(r.status_code, 200)


class ContactFormTests(TestCase):
    """تست فرم تماس: ارسال درست، هانی‌پات، و زبان صحیح ذخیره می‌شود."""

    VALID_DATA = {
        'name': 'علی احمدی',
        'phone': '09121234567',
        'email': 'ali@example.com',
        'subject': 'سوال درباره جراحی',
        'message': 'لطفاً اطلاعات بیشتری بدهید.',
        'website': '',
    }

    def test_valid_post_creates_message(self):
        self.client.post(reverse('main:persian_contact'), self.VALID_DATA)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_valid_post_redirects(self):
        r = self.client.post(reverse('main:persian_contact'), self.VALID_DATA)
        self.assertRedirects(r, '/contact/?sent=1', fetch_redirect_response=False)

    def test_persian_contact_saves_lang_fa(self):
        self.client.post(reverse('main:persian_contact'), self.VALID_DATA)
        self.assertEqual(ContactMessage.objects.first().language, 'fa')

    def test_english_contact_saves_lang_en(self):
        self.client.post(reverse('english:english_contact'), self.VALID_DATA)
        self.assertEqual(ContactMessage.objects.first().language, 'en')

    def test_arabic_contact_saves_lang_ar(self):
        self.client.post(reverse('arabic:arabic_contact'), self.VALID_DATA)
        self.assertEqual(ContactMessage.objects.first().language, 'ar')

    def test_honeypot_blocks_spam(self):
        # اگر فیلد مخفی website پر باشد، پیام نباید ذخیره شود
        data = {**self.VALID_DATA, 'website': 'http://spam.com'}
        self.client.post(reverse('main:persian_contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_missing_required_fields_no_save(self):
        self.client.post(reverse('main:persian_contact'), {'name': '', 'message': ''})
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_sent_flag_shown_after_redirect(self):
        r = self.client.get(reverse('main:persian_contact') + '?sent=1')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['sent'])


class ContextProcessorTests(TestCase):
    """context processor باید در همه صفحات کلیدهای لازم را فراهم کند."""

    def test_context_keys_present_on_home(self):
        r = self.client.get(reverse('main:persian_home'), HTTP_COOKIE='dr_lang=fa')
        self.assertIn('main_clinic', r.context)
        self.assertIn('site_settings', r.context)
        self.assertIn('social_links', r.context)

    def test_context_keys_present_on_about(self):
        r = self.client.get(reverse('main:persian_about'))
        self.assertIn('main_clinic', r.context)
        self.assertIn('social_links', r.context)

    def test_context_keys_present_on_english(self):
        r = self.client.get(reverse('english:english_home'))
        self.assertIn('main_clinic', r.context)
        self.assertIn('social_links', r.context)


class SearchTests(TestCase):
    """جستجو باید query کوتاه را نادیده بگیرد و در بقیه موارد 200 برگرداند."""

    def test_empty_query_returns_200(self):
        r = self.client.get(reverse('main:persian_search'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['total'], 0)

    def test_short_query_ignored(self):
        r = self.client.get(reverse('main:persian_search'), {'q': 'آ'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['total'], 0)

    def test_valid_query_returns_200(self):
        r = self.client.get(reverse('main:persian_search'), {'q': 'چشم'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('posts', r.context)

    def test_english_search_returns_200(self):
        r = self.client.get(reverse('english:english_search'), {'q': 'eye'})
        self.assertEqual(r.status_code, 200)
