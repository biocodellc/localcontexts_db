from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, UserAffiliation

# When a user is saved, send this signal (Create User Profile instance)
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

# When a user is saved, create UserAffiliation instance
@receiver(post_save, sender=User)
def create_useraffiliation(sender, instance, created, **kwargs):
    if created:
        UserAffiliation.objects.create(user=instance)
