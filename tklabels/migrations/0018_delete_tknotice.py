# Generated by Django 3.0.7 on 2021-08-19 20:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0009_auto_20210819_2006'),
        ('tklabels', '0017_auto_20210812_1250'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TKNotice',
        ),
    ]
