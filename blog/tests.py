from django.test import TestCase
from django.urls import reverse
from .models import Post, Category


class BlogListTests(TestCase):
    """صفحه لیست بلاگ در هر سه زبان."""

    def test_persian_blog_list(self):
        r = self.client.get(reverse('blog:persian_blog_list'))
        self.assertEqual(r.status_code, 200)

    def test_english_blog_list(self):
        r = self.client.get(reverse('english_blog:english_blog_list'))
        self.assertEqual(r.status_code, 200)

    def test_arabic_blog_list(self):
        r = self.client.get(reverse('arabic_blog:arabic_blog_list'))
        self.assertEqual(r.status_code, 200)

    def test_unpublished_post_not_in_list(self):
        Post.objects.create(
            title_fa='پست پنهان', title_en='Hidden', title_ar='مخفي',
            slug='hidden-post',
            content_fa='', content_en='', content_ar='',
            is_published=False,
        )
        r = self.client.get(reverse('blog:persian_blog_list'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['page_obj'].paginator.count, 0)


class BlogDetailTests(TestCase):
    """صفحه جزئیات پست: منتشرشده قابل دسترس، پیش‌نویس ۴۰۴ برمی‌گرداند."""

    def setUp(self):
        self.post = Post.objects.create(
            title_fa='آشنایی با بیماری‌های شبکیه',
            title_en='Retinal Diseases Overview',
            title_ar='أمراض الشبكية',
            slug='retinal-diseases',
            content_fa='محتوای فارسی',
            content_en='English content',
            content_ar='المحتوى العربي',
            is_published=True,
        )
        self.draft = Post.objects.create(
            title_fa='پیش‌نویس', title_en='Draft', title_ar='مسودة',
            slug='draft-post',
            content_fa='', content_en='', content_ar='',
            is_published=False,
        )

    def test_published_post_returns_200(self):
        r = self.client.get(reverse('blog:persian_blog_detail', args=['retinal-diseases']))
        self.assertEqual(r.status_code, 200)

    def test_draft_post_returns_404(self):
        r = self.client.get(reverse('blog:persian_blog_detail', args=['draft-post']))
        self.assertEqual(r.status_code, 404)

    def test_nonexistent_slug_returns_404(self):
        r = self.client.get(reverse('blog:persian_blog_detail', args=['does-not-exist']))
        self.assertEqual(r.status_code, 404)

    def test_post_context_has_post(self):
        r = self.client.get(reverse('blog:persian_blog_detail', args=['retinal-diseases']))
        self.assertIn('post', r.context)
        self.assertEqual(r.context['post'].slug, 'retinal-diseases')
