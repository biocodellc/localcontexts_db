from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from communities.models import *
from .models import *

# Sends welcome notification to user that just registered
@receiver(post_save, sender=User)
def create_welcome_message(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(user=instance, title="Welcome", message="You have joined")

# When the instance of invite member form is saved, send target user a notification
@receiver(post_save, sender=InviteMember)
def send_community_invite(sender, instance, created, **kwargs):
    if instance.status == 'sent':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role

        title = "You've been invited by " + str(sender_.get_full_name()) + " to join " + str(instance.community) + "!"
        message= "Join our Community! " + str(instance.community) + "with the role of " + str(role)

        UserNotification.objects.create(user=receiver_, title=title, message=message)

@receiver(post_save, sender=InviteMember)
def accept_community_invite(sender, instance, **kwargs):
    if instance.status == 'accepted':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role

        u = UserCommunity.objects.get(user=receiver_)
        u.communities.add(instance.community)
        u.save()

        title = "You are now a member of " + str(instance.community) + "!"
        message = "Congrats"
        UserNotification.objects.create(user=receiver_, title=title, message=message)

        c = Community.objects.get(id=instance.community.id)

        if role == 'editor':
            c.editors.add(receiver_)
        elif role == 'viewer':
            c.viewers.add(receiver_)

        c.save()

@receiver(post_save, sender=CommunityJoinRequest)
def send_user_join_request(sender, instance, created, **kwargs):
    if created:
        receiver_ = instance.user_to
        sender_ = instance.user_from
        UserNotification.objects.create(user=receiver_, title="User wishes to join", message="This user wants to join community")
