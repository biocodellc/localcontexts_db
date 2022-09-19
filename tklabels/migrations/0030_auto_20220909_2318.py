# Generated by Django 3.1.13 on 2022-09-09 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tklabels', '0029_auto_20220826_1424'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='tklabel',
            index=models.Index(fields=['unique_id', 'created_by', 'community', 'is_approved', 'approved_by', 'audiofile'], name='tklabels_tk_unique__99dad5_idx'),
        ),
    ]