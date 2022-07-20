# Generated by Django 3.1.13 on 2022-07-19 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0127_auto_20220719_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Discoverable', 'Discoverable')], max_length=20, null=True),
        ),
    ]