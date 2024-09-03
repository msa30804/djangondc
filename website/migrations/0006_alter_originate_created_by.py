# Generated by Django 5.1 on 2024-09-02 19:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_rename_ndc_no_originate_hr_no_alter_originate_dept'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='originate',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
