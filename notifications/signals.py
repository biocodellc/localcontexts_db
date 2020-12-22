from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from communities.models import *
from .models import *
from .utils import *

# Sends welcome notification to user that just registered
@receiver(post_save, sender=User)
def create_welcome_message(sender, instance, created, **kwargs):
    if created:
        UserNotification.objects.create(to_user=instance, title="Welcome", message="You have joined", notification_type="welcome")

# When the instance of invite member form is saved, send target user a notification
@receiver(post_save, sender=InviteMember)
def send_community_invite(sender, instance, created, **kwargs):
    if instance.status == 'sent':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role
        community = instance.community

        name = check_full_name(sender_)


        title = "You've been invited by " + str(name) + " to join " + str(community) + "!"
        message= "Join our Community! " + str(community) + "with the role of " + str(role)

        UserNotification.objects.create(to_user=receiver_, title=title, message=message, notification_type="invitation", community=community)

@receiver(post_save, sender=InviteMember)
def accept_community_invite(sender, instance, **kwargs):
    if instance.status == 'accepted':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role
        community = instance.community

        u = UserCommunity.objects.get(user=receiver_)
        u.communities.add(community)
        u.save()

        title = "You are now a member of " + str(community) + "!"
        message = "Congrats"
        
        UserNotification.objects.create(to_user=receiver_, title=title, message=message, notification_type="accept", community=community)

        c = Community.objects.get(id=community.id)

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
        community = instance.target_community

        name = check_full_name(sender_)

        title = str(name) + " wishes to join " + str(community)
        message = "let them join it"

        UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="request", community=community)

@receiver(post_save, sender=Community)
def community_application(sender, instance, created, **kwargs):
    sender_= instance.community_creator
    receiver_= User.objects.get(username="dianalovette")

    name = check_full_name(sender_)

    title = str(name) + " wants to create a community: " + str(instance.community_name)
    message = "Community application."

    if created:
        UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="create", community=instance)

