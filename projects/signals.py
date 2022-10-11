from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Project, ProjectContributors, ProjectCreator
from helpers.models import EntitiesNotified
from notifications.models import ActionNotification

@receiver(post_save, sender=Project)
def create_project_dependencies(sender, instance, created, **kwargs):
    if created:
        if not ProjectContributors.objects.filter(project=instance).exists():
            ProjectContributors.objects.create(project=instance)
        if not EntitiesNotified.objects.filter(project=instance).exists():
            EntitiesNotified.objects.create(project=instance)
        if not ProjectCreator.objects.filter(project=instance).exists():
            ProjectCreator.objects.create(project=instance)

@receiver(post_delete, sender=Project)
def delete_action_notifications(sender, instance, *args, **kwargs):
    if ActionNotification.objects.filter(reference_id=instance.unique_id).exists():
        for notification in ActionNotification.objects.filter(reference_id=instance.unique_id):
            notification.delete()