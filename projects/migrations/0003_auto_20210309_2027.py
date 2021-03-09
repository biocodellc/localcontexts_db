# Generated by Django 3.0.7 on 2021-03-09 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20210224_2219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='principal_investigator',
        ),
        migrations.RemoveField(
            model_name='project',
            name='principal_investigator_affiliation',
        ),
        migrations.RemoveField(
            model_name='project',
            name='source',
        ),
        migrations.AlterField(
            model_name='project',
            name='publication_date',
            field=models.DateField(null=True),
        ),
    ]
