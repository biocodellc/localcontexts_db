# Generated by Django 3.1.13 on 2023-08-16 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0174_auto_20230815_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Contributor', 'Contributor')], max_length=20, null=True),
        ),
    ]