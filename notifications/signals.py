from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from communities.models import InviteMember
from .models import *

# Sends welcome notification to user that just registered
@receiver(post_save, sender=User)
def create_welcome_message(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(user=instance, title="Welcome", message="You have joined")

# When the instance of invite member form is saved, send target user a notification
@receiver(post_save, sender=InviteMember)
def send_community_invite(sender, instance, created, **kwargs):
    sender_ = instance.sender
    receiver_ = instance.receiver
    title = "You've been invited by " + str(sender_.get_full_name()) + " to join " + str(instance.community) + "!"
    message= "Join our Community! " + str(instance.community)

    UserNotification.objects.create(user=receiver_, title=title, message=message)


#TODO: reference

# @receiver(post_save, sender=CommunityInvitation)
# def add_community_member(sender, created, instance, **kwargs):
#     sender_ = instance.sender
#     receiver_ = instance.receiver
#     if instance.status=='accepted':
        # If invitation is accepted
        # Receiver's usercommunity is updated with sender's Community
        # Community is updated with member based on role
        # target_user=UserCommunity.objects.get(username=receiver_.user.username)
        # target_user.communities.add(sender_.community_name)

        # if instance.role=='editor':
        #     sender_.editor.add(receiver_.user)

        # elif instance.role=='viewer':
        #     sender_.viewer.add(receiver_.user)

        # sender_.save()
        # target_user.save()