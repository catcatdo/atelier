from django.db import migrations


def seed_site_setting(apps, schema_editor):
    SiteSetting = apps.get_model('shop', 'SiteSetting')
    if not SiteSetting.objects.exists():
        SiteSetting.objects.create(pk=1)


def reverse_seed(apps, schema_editor):
    SiteSetting = apps.get_model('shop', 'SiteSetting')
    SiteSetting.objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_sitesetting'),
    ]

    operations = [
        migrations.RunPython(seed_site_setting, reverse_seed),
    ]
