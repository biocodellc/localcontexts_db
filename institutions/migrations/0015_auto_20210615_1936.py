# Generated by Django 3.0.7 on 2021-06-15 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0014_auto_20210615_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]