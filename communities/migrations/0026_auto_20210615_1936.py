# Generated by Django 3.0.7 on 2021-06-15 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0025_community_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]