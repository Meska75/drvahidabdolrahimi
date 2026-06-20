from django.db import migrations


INITIAL_STATS = [
    # (key, group_name, label_fa, value_fa, value_en, value_ar, type)
    (
        'stat_years', 'آمار',
        'سال‌های تجربه — عدد',
        '+۲۰', '20+', '+20', 'text',
    ),
    (
        'stat_years_label', 'آمار',
        'سال‌های تجربه — برچسب',
        'سال تجربه بالینی', 'Years of Clinical Experience', 'عامًا من الخبرة السريرية', 'text',
    ),
    (
        'stat_patients', 'آمار',
        'تعداد بیماران — عدد',
        '+۵۰۰۰', '5,000+', '+5,000', 'text',
    ),
    (
        'stat_patients_label', 'آمار',
        'تعداد بیماران — برچسب',
        'بیمار موفق', 'Patients Treated', 'مريض ناجح', 'text',
    ),
    (
        'stat_surgeries', 'آمار',
        'تعداد جراحی‌ها — عدد',
        '+۱۵۰۰', '1,500+', '+1,500', 'text',
    ),
    (
        'stat_surgeries_label', 'آمار',
        'تعداد جراحی‌ها — برچسب',
        'عمل جراحی', 'Surgeries Performed', 'عملية جراحية', 'text',
    ),
    (
        'stat_satisfaction', 'آمار',
        'رضایت بیماران — عدد',
        '۹۸٪', '98%', '98٪', 'text',
    ),
    (
        'stat_satisfaction_label', 'آمار',
        'رضایت بیماران — برچسب',
        'رضایت بیماران', 'Patient Satisfaction', 'رضا المرضى', 'text',
    ),
    (
        'stat_articles', 'آمار',
        'تعداد مقالات علمی — عدد',
        '+۳۰', '30+', '+30', 'text',
    ),
    (
        'stat_articles_label', 'آمار',
        'تعداد مقالات علمی — برچسب',
        'مقاله علمی', 'Scientific Articles', 'مقالة علمية', 'text',
    ),
]


def populate_stats(apps, schema_editor):
    SiteSetting = apps.get_model('main', 'SiteSetting')
    for key, group, label, fa, en, ar, t in INITIAL_STATS:
        SiteSetting.objects.get_or_create(
            key=key,
            defaults={
                'group_name': group,
                'label_fa': label,
                'value_fa': fa,
                'value_en': en,
                'value_ar': ar,
                'type': t,
                'is_editable': True,
            }
        )


def remove_stats(apps, schema_editor):
    SiteSetting = apps.get_model('main', 'SiteSetting')
    keys = [row[0] for row in INITIAL_STATS]
    SiteSetting.objects.filter(key__in=keys).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_sociallinks'),
    ]

    operations = [
        migrations.RunPython(populate_stats, remove_stats),
    ]
