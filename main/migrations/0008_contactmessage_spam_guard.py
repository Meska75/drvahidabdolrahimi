from django.db import migrations, models


def flag_existing_spam(apps, schema_editor):
    """ربات شناخته‌شده و شماره‌های غیرایرانیِ فرم فارسی را از صندوق اصلی جدا می‌کند."""
    Message = apps.get_model('main', 'ContactMessage')
    Message.objects.filter(full_name__iexact='HarryTolcy').update(is_spam=True)
    fold = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
    pending = Message.objects.filter(is_spam=False, language='fa').exclude(phone='')
    for msg in pending.iterator():
        text = (msg.phone or '').translate(fold)
        digits = ''.join(ch for ch in text if ch.isdigit())
        if len(digits) >= 10 and not digits.startswith(('0', '9')):
            msg.is_spam = True
            msg.save(update_fields=['is_spam'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_rename_phones_to_fa_suffix'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='ip_address',
            field=models.CharField(blank=True, max_length=45, verbose_name='آی‌پی'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='is_spam',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text='در فهرست اصلی پنهان است. از فیلتر «اسپم» دیده می‌شود.',
                verbose_name='اسپم',
            ),
        ),
        migrations.RunPython(flag_existing_spam, migrations.RunPython.noop),
    ]
