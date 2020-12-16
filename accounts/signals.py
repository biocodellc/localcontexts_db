from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from communities.models import UserCommunity

# When a user is saved, send this signal (Create User Profile instance)
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

# When a user is saved, create UserCommunity instance
@receiver(post_save, sender=User)
def create_usercommunity(sender, instance, created, **kwargs):
    if created:
        UserCommunity.objects.create(user=instance)

post_save.connect(create_usercommunity, sender=User)