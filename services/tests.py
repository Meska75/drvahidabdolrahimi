from django.test import TestCase
from django.urls import reverse


class ServicePageTests(TestCase):
    """چک می‌کند همه صفحات خدمات در هر سه زبان بدون خطا لود می‌شوند."""

    # ---- فارسی ----
    def test_persian_services_overview(self):
        r = self.client.get(reverse('services:persian_services_overview'))
        self.assertEqual(r.status_code, 200)

    def test_persian_office_services(self):
        r = self.client.get(reverse('services:persian_office_services'))
        self.assertEqual(r.status_code, 200)

    def test_persian_surgery_services(self):
        r = self.client.get(reverse('services:persian_surgery_services'))
        self.assertEqual(r.status_code, 200)

    # ---- انگلیسی ----
    def test_english_services_overview(self):
        r = self.client.get(reverse('english_services:english_services_overview'))
        self.assertEqual(r.status_code, 200)

    def test_english_office_services(self):
        r = self.client.get(reverse('english_services:english_office_services'))
        self.assertEqual(r.status_code, 200)

    def test_english_surgery_services(self):
        r = self.client.get(reverse('english_services:english_surgery_services'))
        self.assertEqual(r.status_code, 200)

    # ---- عربی ----
    def test_arabic_services_overview(self):
        r = self.client.get(reverse('arabic_services:arabic_services_overview'))
        self.assertEqual(r.status_code, 200)

    def test_arabic_office_services(self):
        r = self.client.get(reverse('arabic_services:arabic_office_services'))
        self.assertEqual(r.status_code, 200)

    def test_arabic_surgery_services(self):
        r = self.client.get(reverse('arabic_services:arabic_surgery_services'))
        self.assertEqual(r.status_code, 200)
