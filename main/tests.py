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
    """تست فرم تماس: ارسال درست، هانی‌پات، کپچا، و زبان صحیح ذخیره می‌شود."""

    VALID_DATA = {
        'name': 'علی احمدی',
        'phone': '09121234567',
        'email': 'ali@example.com',
        'subject': 'سوال درباره جراحی',
        'message': 'لطفاً اطلاعات بیشتری بدهید.',
        'website': '',
    }

    def _post(self, url, data=None, code='K7M2P', opened_seconds_ago=30):
        import time
        from main.antispam import issue_opened_at
        from main.captcha import remember
        payload = dict(self.VALID_DATA if data is None else data)
        session = self.client.session
        remember(session, code)
        session.save()
        payload['captcha'] = code
        payload['opened_at'] = issue_opened_at(time.time() - opened_seconds_ago)
        return self.client.post(url, payload)

    def test_valid_post_creates_message(self):
        self._post(reverse('main:persian_contact'))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_valid_post_redirects(self):
        r = self._post(reverse('main:persian_contact'))
        self.assertRedirects(r, '/contact/?sent=1', fetch_redirect_response=False)

    def test_persian_contact_saves_lang_fa(self):
        self._post(reverse('main:persian_contact'))
        self.assertEqual(ContactMessage.objects.first().language, 'fa')

    def test_english_contact_saves_lang_en(self):
        self._post(reverse('english:english_contact'))
        self.assertEqual(ContactMessage.objects.first().language, 'en')

    def test_arabic_contact_saves_lang_ar(self):
        self._post(reverse('arabic:arabic_contact'))
        self.assertEqual(ContactMessage.objects.first().language, 'ar')

    def test_honeypot_blocks_spam(self):
        # اگر فیلد مخفی website پر باشد، پیام نباید ذخیره شود
        data = {**self.VALID_DATA, 'website': 'http://spam.com'}
        self._post(reverse('main:persian_contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_missing_captcha_no_save(self):
        self.client.post(reverse('main:persian_contact'), self.VALID_DATA)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_wrong_captcha_no_save(self):
        from main.captcha import remember
        session = self.client.session
        remember(session, 'AAAAA')
        session.save()
        payload = {**self.VALID_DATA, 'captcha': 'BBBBB'}
        self.client.post(reverse('main:persian_contact'), payload)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_captcha_is_single_use(self):
        self._post(reverse('main:persian_contact'), code='K7M2P')
        self.client.post(
            reverse('main:persian_contact'),
            {**self.VALID_DATA, 'captcha': 'K7M2P'},
        )
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_page_shows_captcha_image(self):
        r = self.client.get(reverse('main:persian_contact'))
        self.assertContains(r, 'data:image/png;base64,')
        self.assertContains(r, 'name="opened_at"')

    def test_too_fast_submit_is_not_saved(self):
        r = self._post(reverse('main:persian_contact'), opened_seconds_ago=0)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertRedirects(r, '/contact/?sent=1', fetch_redirect_response=False)

    def test_missing_opened_at_is_not_saved(self):
        from main.captcha import remember
        session = self.client.session
        remember(session, 'K7M2P')
        session.save()
        r = self.client.post(
            reverse('main:persian_contact'),
            {**self.VALID_DATA, 'captcha': 'K7M2P'},
        )
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertRedirects(r, '/contact/?sent=1', fetch_redirect_response=False)

    def test_bad_persian_phone_is_rejected(self):
        data = {**self.VALID_DATA, 'phone': '87182857515'}
        r = self._post(reverse('main:persian_contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(r, 'تلفن ثابت با کد شهر')

    def test_english_accepts_international_phone(self):
        data = {**self.VALID_DATA, 'phone': '+14155552671'}
        self._post(reverse('english:english_contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertFalse(ContactMessage.objects.first().is_spam)

    def test_rate_limit_blocks_third_message(self):
        for _ in range(2):
            ContactMessage.objects.create(
                full_name='بیمار',
                message='قبلی',
                ip_address='127.0.0.1',
            )
        r = self._post(reverse('main:persian_contact'))
        self.assertEqual(ContactMessage.objects.count(), 2)
        self.assertContains(r, 'چند پیام پشت‌سرهم')

    def test_repeated_name_is_quarantined(self):
        for _ in range(3):
            ContactMessage.objects.create(
                full_name='HarryTolcy',
                message='spam',
                ip_address='203.0.113.9',
            )
        data = {**self.VALID_DATA, 'name': 'HarryTolcy', 'phone': ''}
        self._post(reverse('main:persian_contact'), data)
        saved = ContactMessage.objects.get(ip_address='127.0.0.1')
        self.assertTrue(saved.is_spam)

    def test_appointment_checkbox_is_saved(self):
        data = {**self.VALID_DATA, 'wants_appointment': 'on'}
        self._post(reverse('main:persian_contact'), data)
        self.assertTrue(ContactMessage.objects.get().wants_appointment)

    def test_without_checkbox_is_not_appointment(self):
        self._post(reverse('main:persian_contact'))
        self.assertFalse(ContactMessage.objects.get().wants_appointment)

    def test_appointment_without_phone_is_rejected(self):
        data = {**self.VALID_DATA, 'phone': '', 'wants_appointment': 'on'}
        r = self._post(reverse('main:persian_contact'), data)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(r, 'برای گرفتن وقت')

    def test_appointment_admin_lists_only_requests(self):
        from django.contrib.auth.models import User
        User.objects.create_superuser('desk', 'desk@example.com', 'pass12345')
        ContactMessage.objects.create(
            full_name='نوبت‌گیر', message='وقت می‌خواهم', phone='09120000000',
            wants_appointment=True,
        )
        ContactMessage.objects.create(
            full_name='فقط پیام', message='سوال دارم', wants_appointment=False,
        )
        self.client.login(username='desk', password='pass12345')
        page = self.client.get('/admin/main/appointmentrequest/')
        self.assertContains(page, 'نوبت‌گیر')
        self.assertNotContains(page, 'فقط پیام')

    def test_admin_inbox_hides_spam_by_default(self):
        from django.contrib.auth.models import User
        User.objects.create_superuser('admin', 'a@example.com', 'pass12345')
        ContactMessage.objects.create(full_name='بیمار واقعی', message='سلام', is_spam=False)
        ContactMessage.objects.create(full_name='HarryTolcy', message='spam', is_spam=True)
        self.client.login(username='admin', password='pass12345')
        inbox = self.client.get('/admin/main/contactmessage/')
        self.assertContains(inbox, 'بیمار واقعی')
        self.assertNotContains(inbox, 'HarryTolcy')
        spam = self.client.get('/admin/main/contactmessage/?inbox=spam')
        self.assertContains(spam, 'HarryTolcy')

    def test_captcha_refresh_returns_new_image(self):
        r = self.client.get(reverse('main:contact_captcha'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['image'].startswith('data:image/png;base64,'))

    def test_missing_required_fields_no_save(self):
        self._post(reverse('main:persian_contact'), {'name': '', 'message': '', 'website': ''})
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
