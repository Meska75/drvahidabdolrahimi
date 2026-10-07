from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_contactmessage_spam_guard'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='wants_appointment',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text='اگر تیک «وقت گرفتن» خورده باشد، در فهرست درخواست نوبت هم دیده می‌شود.',
                verbose_name='درخواست نوبت',
            ),
        ),
    ]
