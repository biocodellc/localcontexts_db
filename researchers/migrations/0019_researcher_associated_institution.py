# Generated by Django 3.0.7 on 2021-05-20 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0018_auto_20210520_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='researcher',
            name='associated_institution',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]