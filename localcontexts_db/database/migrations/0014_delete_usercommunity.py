# Generated by Django 3.1 on 2020-09-08 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0013_delete_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserCommunity',
        ),
    ]
