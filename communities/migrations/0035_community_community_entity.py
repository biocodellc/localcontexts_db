# Generated by Django 3.0.7 on 2021-08-24 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0034_auto_20210824_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='community_entity',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
