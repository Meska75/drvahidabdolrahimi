# Rename phone_1/phone_2 → phone_1_fa/phone_2_fa (هم‌تراز با address_fa)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_doctorclinic_phone_i18n'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctorclinic',
            old_name='phone_1',
            new_name='phone_1_fa',
        ),
        migrations.RenameField(
            model_name='doctorclinic',
            old_name='phone_2',
            new_name='phone_2_fa',
        ),
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_1_fa',
            field=models.CharField(blank=True, max_length=30, verbose_name='تلفن اول فارسی'),
        ),
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_2_fa',
            field=models.CharField(blank=True, max_length=30, verbose_name='تلفن دوم فارسی'),
        ),
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_1_en',
            field=models.CharField(blank=True, max_length=30, verbose_name='Phone 1 English'),
        ),
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_2_en',
            field=models.CharField(blank=True, max_length=30, verbose_name='Phone 2 English'),
        ),
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_1_ar',
            field=models.CharField(blank=True, max_length=30, verbose_name='هاتف ١ عربي'),
        ),
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_2_ar',
            field=models.CharField(blank=True, max_length=30, verbose_name='هاتف ٢ عربي'),
        ),
    ]
