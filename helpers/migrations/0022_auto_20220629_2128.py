# Generated by Django 3.1.13 on 2022-06-29 21:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0032_remove_researcher_projects'),
        ('helpers', '0021_opentocollaboratenoticeurl'),
    ]

    operations = [
        migrations.RenameField(
            model_name='institutionnotice',
            old_name='attribution_incomplete_default_text',
            new_name='default_text',
        ),
        migrations.RenameField(
            model_name='institutionnotice',
            old_name='attribution_incomplete_img_url',
            new_name='img_url',
        ),
        migrations.RenameField(
            model_name='institutionnotice',
            old_name='attribution_incomplete_svg_url',
            new_name='svg_url',
        ),
        migrations.AddField(
            model_name='institutionnotice',
            name='researcher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='researchers.researcher'),
        ),
    ]
