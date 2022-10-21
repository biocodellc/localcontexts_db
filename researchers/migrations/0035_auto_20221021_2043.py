# Generated by Django 3.1.13 on 2022-10-21 20:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0034_auto_20220909_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researcher',
            name='description',
            field=models.TextField(null=True, validators=[django.core.validators.MaxLengthValidator(200)]),
        ),
    ]
