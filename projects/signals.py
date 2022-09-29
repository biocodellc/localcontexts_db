from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, ProjectContributors, ProjectCreator
from helpers.models import EntitiesNotified

@receiver(post_save, sender=Project)
def create_project_dependencies(sender, instance, created, **kwargs):
    if created:
        if not ProjectContributors.objects.filter(project=instance).exists():
            ProjectContributors.objects.create(project=instance)
        if not EntitiesNotified.objects.filter(project=instance).exists():
            EntitiesNotified.objects.create(project=instance)
        if not ProjectCreator.objects.filter(project=instance).exists():
            ProjectCreator.objects.create(project=instance)