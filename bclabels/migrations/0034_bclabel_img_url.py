# Generated by Django 3.0.7 on 2021-07-29 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bclabels', '0033_bcnotice_img_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='bclabel',
            name='img_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
