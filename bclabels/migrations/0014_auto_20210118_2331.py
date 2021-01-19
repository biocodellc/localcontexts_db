# Generated by Django 3.0.7 on 2021-01-18 23:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0004_auto_20210118_2306'),
        ('institutions', '0004_delete_userinstitution'),
        ('bclabels', '0013_auto_20210118_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='bcnotice',
            name='placed_by_institution',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='institutions.Institution'),
        ),
        migrations.AddField(
            model_name='bcnotice',
            name='placed_by_researcher',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='researchers.Researcher'),
        ),
    ]
