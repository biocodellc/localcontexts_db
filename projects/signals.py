from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, ProjectContributors

@receiver(post_save, sender=Project)
def create_contributors(sender, instance, created, **kwargs):
    if created:
        if not ProjectContributors.objects.filter(project=instance).exists():
            ProjectContributors.objects.create(project=instance)