# Generated by Django 3.0.7 on 2021-05-05 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_auto_20210429_0023'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_image',
            field=models.ImageField(blank=True, null=True, upload_to='users/project-images'),
        ),
    ]
