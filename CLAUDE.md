به فایل CLAUDE.md این اطلاعات رو اضافه کن:

## اطلاعات پروژه
- پروژه: وبسایت رسمی دکتر عبدالرحیمی - متخصص چشم‌پزشکی
- سه‌زبانه: فارسی، انگلیسی، عربی
- هاستینگ: سرور ایرانی (آروان یا لیارا)

## صفحات مورد نیاز (فاز ۱)
- صفحه انتخاب زبان (landing page)
- صفحه معرفی پزشک (about)
- صفحه خدمات مطب (کارت‌های کوچک)
- صفحه خدمات جراحی (کارت‌های کوچک)
- صفحه تیم و همکاران مطب
- آلبوم تصاویر
- صفحه تماس با ما
- پنل ادمین کامل (CMS)

## قوانین کدنویسی
- کامنت‌های کد به فارسی
- RTL برای فارسی و عربی
- Mobile-first طراحی
- Bootstrap برای استایل


# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate the virtual environment (Windows)
env\Scripts\activate

# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Run tests
python manage.py test

# Run tests for a single app
python manage.py test main
python manage.py test services

# Collect static files (for production)
python manage.py collectstatic
```

## Architecture

This is a **Django 5.2.1** website for Dr. Vahid Abdolrahimi — a Persian-language medical/doctor's office site.

### Apps

- **`main/`** — Core pages: home, about, contact. URL prefix: `/` (no prefix).
- **`services/`** — Service pages: office services, surgery services. URL prefix: `/services/`.

### URL routing

Root URLs are in `config/urls.py`, which delegates to `main.urls` (namespace `main`) and `services.urls` (namespace `services`). Use `{% url "main:persian_home" %}` style references in templates.

### Templates

All templates live under `templates/persian/` and extend `templates/persian/persian_base.html`. Page templates are organized into subdirectories:
- `templates/persian/persian_main/` — pages served by the `main` app
- `templates/persian/persian_services/` — pages served by the `services` app

The base template (`persian_base.html`) includes Bootstrap 4.1.3, Font Awesome 4.7.0, Owl Carousel, and a datetime picker. It defines a single `{% block content %}` for page-specific content.

### Static files

- **Source**: `static_files/` (CSS, JS, fonts, images) — referenced in templates via `{% load static %}` / `{% static '...' %}`
- **Output**: `static/` (`STATIC_ROOT`) — only used after running `collectstatic` for production

Media uploads are configured to `media/` (`MEDIA_ROOT`).

### Database

SQLite3 (`db.sqlite3`). Neither `main` nor `services` app has models yet — the database only holds Django's built-in tables.
