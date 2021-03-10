# Generated by Django 3.0.7 on 2021-02-24 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='contributors',
        ),
        migrations.AddField(
            model_name='projectcontributors',
            name='project',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.Project'),
        ),
    ]
