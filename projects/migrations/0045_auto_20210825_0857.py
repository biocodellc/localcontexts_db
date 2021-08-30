# Generated by Django 3.0.7 on 2021-08-25 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bclabels', '0037_delete_bcnotice'),
        ('projects', '0044_auto_20210824_1253'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='tklabels',
            new_name='tk_labels',
        ),
        migrations.RemoveField(
            model_name='project',
            name='bclabels',
        ),
        migrations.AddField(
            model_name='project',
            name='bc_labels',
            field=models.ManyToManyField(blank=True, related_name='project_bclabels', to='bclabels.BCLabel', verbose_name='BC Labels'),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Discoverable', 'Discoverable')], max_length=20, null=True),
        ),
    ]