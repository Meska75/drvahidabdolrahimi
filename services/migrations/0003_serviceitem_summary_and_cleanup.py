import re
from django.db import migrations, models


def strip_html(text):
    """تگ‌های HTML و فاصله‌های اضافه را پاک می‌کند"""
    text = re.sub(r'<[^>]+>', ' ', text or '')
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def migrate_descriptions(apps, schema_editor):
    """محتوای HTML قدیمی را به متن ساده تبدیل می‌کند"""
    ServiceItem = apps.get_model('services', 'ServiceItem')
    for item in ServiceItem.objects.all():
        # description_fa ممکن است HTML داشته باشد — پاک می‌کنیم
        clean_fa = strip_html(item.description_fa)[:250]
        clean_en = strip_html(item.description_en)[:250]
        clean_ar = strip_html(item.description_ar)[:250]
        item.description_fa = clean_fa
        item.description_en = clean_en
        item.description_ar = clean_ar
        # summary را از ۹۰ کاراکتر اول description پر می‌کنیم
        item.summary_fa = clean_fa[:90]
        item.summary_en = clean_en[:90]
        item.summary_ar = clean_ar[:90]
        item.save(update_fields=[
            'description_fa', 'description_en', 'description_ar',
            'summary_fa', 'summary_en', 'summary_ar',
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_serviceitem_type_direct'),
    ]

    operations = [
        # ۱. فیلدهای summary اضافه می‌شوند
        migrations.AddField(
            model_name='serviceitem',
            name='summary_fa',
            field=models.CharField(blank=True, max_length=90,
                                   verbose_name='متن خلاصه — فارسی',
                                   help_text='حداکثر ۹۰ کاراکتر — نمایش در کارت‌های صفحه اصلی'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='summary_en',
            field=models.CharField(blank=True, max_length=90,
                                   verbose_name='Summary — English',
                                   help_text='Max 90 characters — shown on home page cards'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='summary_ar',
            field=models.CharField(blank=True, max_length=90,
                                   verbose_name='الملخص — عربي',
                                   help_text='الحد الأقصى ٩٠ حرفًا'),
        ),
        # ۲. description تبدیل به CharField با max_length می‌شود
        migrations.AlterField(
            model_name='serviceitem',
            name='description_fa',
            field=models.CharField(blank=True, max_length=250,
                                   verbose_name='توضیح کوتاه — فارسی',
                                   help_text='حداکثر ۲۵۰ کاراکتر — نمایش در صفحه خدمات'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='description_en',
            field=models.CharField(blank=True, max_length=250,
                                   verbose_name='Description — English',
                                   help_text='Max 250 characters — shown on services page'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='description_ar',
            field=models.CharField(blank=True, max_length=250,
                                   verbose_name='الوصف — عربي',
                                   help_text='الحد الأقصى ٢٥٠ حرفًا'),
        ),
        # ۳. محتوای HTML پاک می‌شود و summary پر می‌شود
        migrations.RunPython(migrate_descriptions, migrations.RunPython.noop),
        # ۴. icon_class حذف می‌شود
        migrations.RemoveField(
            model_name='serviceitem',
            name='icon_class',
        ),
    ]
