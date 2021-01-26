from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from communities.models import Community
from bclabels.models import BCNotice
from .models import Project

# Creates a notice when a Project is created
@receiver(post_save, sender=Project)
def create_bc_notice(sender, instance, created, **kwargs):
    if created:
        BCNotice.objects.create(project=instance)