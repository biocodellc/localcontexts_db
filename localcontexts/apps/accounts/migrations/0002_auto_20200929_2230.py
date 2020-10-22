# Generated by Django 3.0.7 on 2020-09-29 22:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='job_title',
            field=models.CharField(max_length=80, verbose_name='job title'),
        ),
        migrations.CreateModel(
            name='UserCommunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('communities', models.ManyToManyField(to='accounts.Community')),
            ],
            options={
                'verbose_name': 'User Community',
                'verbose_name_plural': 'User Communities',
            },
        ),
    ]
