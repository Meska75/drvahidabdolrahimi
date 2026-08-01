# Generated manually — جداسازی شماره تلفن فارسی / انگلیسی / عربی

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_sitesetting_options_alter_doctorclinic_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_1',
            field=models.CharField(blank=True, max_length=30, verbose_name='تلفن اول (فارسی)'),
        ),
        migrations.AlterField(
            model_name='doctorclinic',
            name='phone_2',
            field=models.CharField(blank=True, max_length=30, verbose_name='تلفن دوم (فارسی)'),
        ),
        migrations.AddField(
            model_name='doctorclinic',
            name='phone_1_en',
            field=models.CharField(blank=True, max_length=30, verbose_name='Phone 1 (English)'),
        ),
        migrations.AddField(
            model_name='doctorclinic',
            name='phone_2_en',
            field=models.CharField(blank=True, max_length=30, verbose_name='Phone 2 (English)'),
        ),
        migrations.AddField(
            model_name='doctorclinic',
            name='phone_1_ar',
            field=models.CharField(blank=True, max_length=30, verbose_name='هاتف ۱ (عربي)'),
        ),
        migrations.AddField(
            model_name='doctorclinic',
            name='phone_2_ar',
            field=models.CharField(blank=True, max_length=30, verbose_name='هاتف ۲ (عربي)'),
        ),
    ]
