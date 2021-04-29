# Generated by Django 3.0.7 on 2021-04-27 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0010_projectcomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectcomment',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_sender', to=settings.AUTH_USER_MODEL),
        ),
    ]
