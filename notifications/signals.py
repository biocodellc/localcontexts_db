from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver, Signal
from django.contrib.auth.models import User, Group
from communities.models import *
from .models import *
from .utils import *
from django.conf import settings

# When the instance of invite member form is saved, send target user a notification
@receiver(post_save, sender=InviteMember)
def send_community_invite(sender, instance, created, **kwargs):
    if instance.status == 'sent':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role
        ref = instance.id
        msg = instance.message
        name = check_full_name(sender_)

        if instance.community:
            community = instance.community
            title = str(name) + " has invited you to join " + str(community) + "."

            if msg:
                message = msg
            else:
                message= "You've been invited to join " + str(community) + " with the role of " + str(role)
            UserNotification.objects.create(to_user=receiver_, title=title, message=message, notification_type="Invitation", community=community, reference_id=ref, role=role)

        if instance.institution:
            institution = instance.institution
            title = str(name) + " has invited you to join " + str(institution) + "."

            if msg:
                message = msg
            else:
                message= "You've been invited to join " + str(institution) + " with the role of " + str(role)
            UserNotification.objects.create(to_user=receiver_, title=title, message=message, notification_type="Invitation", institution=institution, reference_id=ref, role=role)


# When an invitation to a community or institution is accepted, send target a notification
@receiver(post_save, sender=InviteMember)
def accept_community_invite(sender, instance, **kwargs):
    if instance.status == 'accepted':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role
        ref = instance.id

        if instance.community:
            community = instance.community

            # Lets user know they are now a member
            title = "You are now a member of " + str(community) + "."
            message = "You now have access to " + str(community) + "'s notices and labels."
            
            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Accept", community=community, reference_id=ref)

            # Lets sender know their invitation was accepted
            title2 = str(check_full_name(receiver_)) + " has accepted your invitation to join " + str(community) + "!"
            message2 = str(check_full_name(receiver_)) + " is now a member of " + str(community)
            
            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title2, message=message2, notification_type="Accept", community=community, reference_id=ref)

            instance.delete() # Deletes the invitation after it has been accepted

        if instance.institution:
            institution = instance.institution

            # Lets user know they are now a member
            title = "You are now a member of " + str(institution) + "."
            message = "You now have access to " + str(institution) + "'s notices and projects."
            
            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Accept", institution=institution, reference_id=ref)

            # Lets sender know their invitation was accepted
            title2 = str(check_full_name(receiver_)) + " has accepted your invitation to join " + str(institution) + "."
            message2 = str(check_full_name(receiver_)) + " is now a member of " + str(institution)
            
            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title2, message=message2, notification_type="Accept", institution=institution, reference_id=ref)

            instance.delete() # Deletes the invitation after it has been accepted


# Send notification when user wishes to join a community or institution
@receiver(post_save, sender=JoinRequest)
def send_user_join_request(sender, instance, created, **kwargs):
    if created:
        receiver_ = instance.user_to
        sender_ = instance.user_from
        ref = instance.id

        name = check_full_name(sender_)

        if instance.community:
            community = instance.community

            title = str(name) + " wishes to join " + str(community)
            message = str(name) + " is requesting to join " + str(community)

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Request", community=community, reference_id=ref)
        if instance.institution:
            institution = instance.institution

            title = str(name) + " wishes to join " + str(institution)
            message = str(name) + " is requesting to join " + str(institution)

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Request", institution=institution, reference_id=ref)


# Send notification when a user's join request has been accepted and they are now part of a community or institution
@receiver(post_save, sender=JoinRequest)
def accept_user_join_request(sender, instance, created, **kwargs):
    if instance.status == 'accepted':
        receiver_ = instance.user_to
        sender_ = instance.user_from
        ref = instance.id

        if instance.community:
            community = instance.community

            # Message to user requesting to join after request has been approved.
            title = "You are now a member of " + str(community)
            message = "Your request to join " + str(community) + " has been accepted and you are now a member"

            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title, message=message, notification_type="Accept", community=community, reference_id=ref)

            # Message to user accepting the join request letting them know user is now a community member.
            title2 = str(check_full_name(sender_)) + " is now a member of " + str(community)
            message2 = str(check_full_name(sender_)) + " is now a member of " + str(community) + "." + " They will now have access to " + str(community) + "'s notices and labels"

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title2, message=message2, notification_type="Accept", community=community, reference_id=ref)
            instance.delete() # Deletes the request when it has been accepted

        if instance.institution:
            institution = instance.institution

            # Message to user requesting to join after request has been approved.
            title = "You are now a member of " + str(institution)
            message = "Your request to join " + str(institution) + " has been accepted and you are now a member"

            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title, message=message, notification_type="Accept", institution=institution, reference_id=ref)

            # Message to user accepting the join request letting them know user is now a institution member.
            title2 = str(check_full_name(sender_)) + " is now a member of " + str(institution)
            message2 = str(check_full_name(sender_)) + " is now a member of " + str(institution) + "." + " They will now have access to " + str(institution) + "'s notices and projects"

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title2, message=message2, notification_type="Accept", institution=institution, reference_id=ref)
            instance.delete() # Deletes the request when it has been accepted

# Sends Site admin notifiation with request to create community
@receiver(post_save, sender=Community)
def community_application(sender, instance, created, **kwargs):
    creator = instance.community_creator
    admin = User.objects.get(email=settings.SITE_ADMIN_EMAIL)

    name = check_full_name(creator)

    title = str(name) + " wants to create a community: " + str(instance.community_name)
    message = str(name) + " wants to create a community: " + str(instance.community_name)

    if created:
        UserNotification.objects.create(to_user=admin, from_user=creator, title=title, message=message, notification_type="Create", community=instance)