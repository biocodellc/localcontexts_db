# Generated by Django 3.0.7 on 2021-08-19 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('helpers', '0007_auto_20210819_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticecomment',
            name='notice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notice_comment', to='helpers.Notice'),
        ),
        migrations.AddField(
            model_name='noticestatus',
            name='notice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notice_status', to='helpers.Notice'),
        ),
    ]