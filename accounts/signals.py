from sqlite3 import connect
from venv import create
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from communities.models import Community
from helpers.models import Connections
from institutions.models import Institution
from researchers.models import Researcher
from .models import Profile, UserAffiliation

# When a user is saved, send this signal (Create User Profile and Affiliation instances)
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        UserAffiliation.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.user_profile.save()

@receiver(post_save, sender=Community)
def create_community_connection(sender, instance, created, **kwargs):
    if created:
        Connections.objects.create(community=instance)

@receiver(post_save, sender=Institution)
def create_institution_connection(sender, instance, created, **kwargs):
    if created:
        Connections.objects.create(institution=instance)

@receiver(post_save, sender=Researcher)
def create_researcher_connection(sender, instance, created, **kwargs):
    if created:
        Connections.objects.create(researcher=instance)
