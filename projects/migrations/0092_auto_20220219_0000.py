# Generated by Django 3.1.13 on 2022-02-19 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0091_auto_20220218_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_privacy',
            field=models.CharField(choices=[('Public', 'Public'), ('Private', 'Private'), ('Discoverable', 'Discoverable')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_type',
            field=models.CharField(choices=[('Item', 'Item'), ('Collection', 'Collection'), ('Samples', 'Samples'), ('Expedition', 'Expedition'), ('Publication', 'Publication'), ('Exhibition', 'Exhibition'), ('Other', 'Other')], max_length=20, null=True),
        ),
    ]