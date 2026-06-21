from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count, Q, F
from django.db.models.functions import ExtractYear
from .models import Post, Category, Comment
from .forms import CommentForm

POSTS_PER_PAGE = 10


def _parse_int(val):
    try:
        return int(val) if val else None
    except ValueError:
        return None


def _sidebar_data():
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    ).order_by('sort_order', 'id')

    years = (
        Post.objects.filter(is_published=True)
        .annotate(year=ExtractYear('published_at'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('-year')
    )

    total_posts   = Post.objects.filter(is_published=True).count()
    popular_posts = Post.objects.filter(is_published=True).order_by('-views_count')[:3]

    return categories, years, total_posts, popular_posts


# ===== فارسی =====

def persian_blog_list(request):
    active_cat  = _parse_int(request.GET.get('cat'))
    active_year = _parse_int(request.GET.get('year'))

    qs = Post.objects.filter(is_published=True)
    if active_cat:
        qs = qs.filter(category_id=active_cat)
    if active_year:
        qs = qs.filter(published_at__year=active_year)

    page_obj = Paginator(qs, POSTS_PER_PAGE).get_page(request.GET.get('page'))
    categories, years, total_posts, popular_posts = _sidebar_data()

    return render(request, 'persian/persian_blog/persian_blog_list.html', {
        'posts':         page_obj,
        'page_obj':      page_obj,
        'categories':    categories,
        'years':         years,
        'active_cat':    active_cat,
        'active_year':   active_year,
        'total_posts':   total_posts,
        'popular_posts': popular_posts,
    })


def persian_blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    # شمارش اتمیک — جلوگیری از race condition زیر بار همزمان
    Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    post.views_count += 1  # هماهنگ‌سازی مقدار در حافظه برای نمایش در همین صفحه
    related = Post.objects.filter(is_published=True, category=post.category).exclude(pk=post.pk)[:3]
    comments = post.comments.filter(is_approved=True)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.language = 'fa'
            c.save()
            return redirect(request.path + '?commented=1')
    else:
        form = CommentForm()

    return render(request, 'persian/persian_blog/persian_blog_detail.html', {
        'post':      post,
        'related':   related,
        'comments':  comments,
        'form':      form,
        'commented': request.GET.get('commented') == '1',
    })


# ===== English =====

def english_blog_list(request):
    active_cat  = _parse_int(request.GET.get('cat'))
    active_year = _parse_int(request.GET.get('year'))

    qs = Post.objects.filter(is_published=True)
    if active_cat:
        qs = qs.filter(category_id=active_cat)
    if active_year:
        qs = qs.filter(published_at__year=active_year)

    page_obj = Paginator(qs, POSTS_PER_PAGE).get_page(request.GET.get('page'))
    categories, years, total_posts, popular_posts = _sidebar_data()

    return render(request, 'english/english_blog/english_blog_list.html', {
        'posts':         page_obj,
        'page_obj':      page_obj,
        'categories':    categories,
        'years':         years,
        'active_cat':    active_cat,
        'active_year':   active_year,
        'total_posts':   total_posts,
        'popular_posts': popular_posts,
    })


def english_blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    # شمارش اتمیک — جلوگیری از race condition زیر بار همزمان
    Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    post.views_count += 1  # هماهنگ‌سازی مقدار در حافظه برای نمایش در همین صفحه
    related = Post.objects.filter(is_published=True, category=post.category).exclude(pk=post.pk)[:3]
    comments = post.comments.filter(is_approved=True)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.language = 'en'
            c.save()
            return redirect(request.path + '?commented=1')
    else:
        form = CommentForm()

    return render(request, 'english/english_blog/english_blog_detail.html', {
        'post':      post,
        'related':   related,
        'comments':  comments,
        'form':      form,
        'commented': request.GET.get('commented') == '1',
    })


# ===== العربية =====

def arabic_blog_list(request):
    active_cat  = _parse_int(request.GET.get('cat'))
    active_year = _parse_int(request.GET.get('year'))

    qs = Post.objects.filter(is_published=True)
    if active_cat:
        qs = qs.filter(category_id=active_cat)
    if active_year:
        qs = qs.filter(published_at__year=active_year)

    page_obj = Paginator(qs, POSTS_PER_PAGE).get_page(request.GET.get('page'))
    categories, years, total_posts, popular_posts = _sidebar_data()

    return render(request, 'arabic/arabic_blog/arabic_blog_list.html', {
        'posts':         page_obj,
        'page_obj':      page_obj,
        'categories':    categories,
        'years':         years,
        'active_cat':    active_cat,
        'active_year':   active_year,
        'total_posts':   total_posts,
        'popular_posts': popular_posts,
    })


def arabic_blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    # شمارش اتمیک — جلوگیری از race condition زیر بار همزمان
    Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    post.views_count += 1  # هماهنگ‌سازی مقدار در حافظه برای نمایش در همین صفحه
    related = Post.objects.filter(is_published=True, category=post.category).exclude(pk=post.pk)[:3]
    comments = post.comments.filter(is_approved=True)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.language = 'ar'
            c.save()
            return redirect(request.path + '?commented=1')
    else:
        form = CommentForm()

    return render(request, 'arabic/arabic_blog/arabic_blog_detail.html', {
        'post':      post,
        'related':   related,
        'comments':  comments,
        'form':      form,
        'commented': request.GET.get('commented') == '1',
    })
