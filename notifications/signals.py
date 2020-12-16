from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *

# Sends welcome notification to user that just registered
@receiver(post_save, sender=User)
def create_welcome_message(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(user=instance, title="Welcome", message="You have joined")

post_save.connect(create_welcome_message, sender=User)