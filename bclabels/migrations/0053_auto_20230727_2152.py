# Generated by Django 3.1.13 on 2023-07-27 21:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bclabels', '0052_bclabel_last_edited_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bclabel',
            name='last_edited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bclabel_last_edited_by', to=settings.AUTH_USER_MODEL),
        ),
    ]