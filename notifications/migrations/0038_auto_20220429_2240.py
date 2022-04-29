# Generated by Django 3.1.13 on 2022-04-29 22:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0037_auto_20220428_2319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionnotification',
            name='notification_type',
            field=models.CharField(blank=True, choices=[('Labels', 'labels'), ('Connections', 'connections'), ('Activity', 'activity'), ('Projects', 'projects'), ('Members', 'members')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='actionnotification',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='actionnotification',
            name='viewed',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='from_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='message',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='notification_type',
            field=models.CharField(blank=True, choices=[('Welcome', 'welcome'), ('Invitation', 'invitation'), ('Request', 'request'), ('Approval', 'approval'), ('Accept', 'accept')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='to_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usernotification',
            name='viewed',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
