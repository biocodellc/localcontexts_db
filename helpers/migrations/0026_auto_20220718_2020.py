# Generated by Django 3.1.13 on 2022-07-18 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0025_auto_20220706_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opentocollaboratenoticeurl',
            name='url',
            field=models.URLField(null=True),
        ),
    ]