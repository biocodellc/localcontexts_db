# Generated by Django 3.1.13 on 2022-09-09 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0043_community_native_land_slug'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='community',
            index=models.Index(fields=['community_creator', 'image'], name='communities_communi_4fae5c_idx'),
        ),
        migrations.AddIndex(
            model_name='invitemember',
            index=models.Index(fields=['sender', 'receiver', 'community', 'institution'], name='communities_sender__b17605_idx'),
        ),
        migrations.AddIndex(
            model_name='joinrequest',
            index=models.Index(fields=['user_from', 'user_to', 'community', 'institution'], name='communities_user_fr_5419d5_idx'),
        ),
    ]