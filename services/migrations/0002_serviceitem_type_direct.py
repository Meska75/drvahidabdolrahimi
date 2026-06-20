from django.db import migrations, models


def copy_type_from_category(apps, schema_editor):
    """مقدار type را از ServiceCategory به ServiceItem منتقل می‌کند"""
    ServiceItem = apps.get_model('services', 'ServiceItem')
    for item in ServiceItem.objects.select_related('category').all():
        if item.category_id:
            item.type = item.category.type
            item.save(update_fields=['type'])


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        # ۱. فیلد type را با مقدار پیش‌فرض اضافه می‌کنیم
        migrations.AddField(
            model_name='serviceitem',
            name='type',
            field=models.CharField(
                choices=[('office', 'خدمات مطب'), ('surgery', 'خدمات جراحی')],
                default='office',
                max_length=10,
                verbose_name='نوع خدمت',
            ),
        ),
        # ۲. داده‌های موجود را از category.type کپی می‌کنیم
        migrations.RunPython(copy_type_from_category, migrations.RunPython.noop),
        # ۳. FK دسته‌بندی را حذف می‌کنیم
        migrations.RemoveField(
            model_name='serviceitem',
            name='category',
        ),
        # ۴. جدول ServiceCategory را حذف می‌کنیم
        migrations.DeleteModel(
            name='ServiceCategory',
        ),
    ]
