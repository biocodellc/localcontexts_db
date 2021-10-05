# Generated by Django 3.0.7 on 2021-10-01 19:16

from django.db import migrations, models
import researchers.models


class Migration(migrations.Migration):

    dependencies = [
        ('researchers', '0028_remove_researcher_contact_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researcher',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=researchers.models.researcher_img_path),
        ),
    ]