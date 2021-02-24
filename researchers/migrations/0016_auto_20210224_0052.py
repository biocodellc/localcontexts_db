# Generated by Django 3.0.7 on 2021-02-24 00:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bclabels', '0019_auto_20210224_0052'),
        ('researchers', '0015_project_project_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectcontributors',
            name='community',
        ),
        migrations.RemoveField(
            model_name='projectcontributors',
            name='institution',
        ),
        migrations.RemoveField(
            model_name='projectcontributors',
            name='project',
        ),
        migrations.RemoveField(
            model_name='researcher',
            name='projects',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
        migrations.DeleteModel(
            name='ProjectContributors',
        ),
    ]
