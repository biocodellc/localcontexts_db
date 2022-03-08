from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from communities.models import *
from .models import *
from .utils import *
from django.conf import settings
from helpers.emails import send_membership_email

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
            title = f"{name} has invited you to join {community}."

            if msg:
                message = msg
            else:
                message= f"You've been invited to join {community} with the role of {role}"
            UserNotification.objects.create(to_user=receiver_, title=title, message=message, notification_type="Invitation", community=community, reference_id=ref, role=role)

        if instance.institution:
            institution = instance.institution
            title = f"{name} has invited you to join {institution}."

            if msg:
                message = msg
            else:
                message= f"You've been invited to join {institution} with the role of {role}."
            UserNotification.objects.create(to_user=receiver_, title=title, message=message, notification_type="Invitation", institution=institution, reference_id=ref, role=role)


# When an invitation to a community or institution is accepted, send target a notification
@receiver(post_save, sender=InviteMember)
def accept_community_invite(sender, instance, **kwargs):
    if instance.status == 'accepted':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role
        ref = instance.id
        receiver_name = check_full_name(receiver_)

        if instance.community:
            community = instance.community

            # Lets user know they are now a member
            title = f"You are now a member of {community}."
            message = f"You now have access to {community}'s Projects and Labels."
            
            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Accept", community=community, reference_id=ref)
            
            # Send email letting user know they are a member
            # send_membership_email(community, receiver_, role)

            # Lets sender know their invitation was accepted
            title2 = f"{receiver_name} has accepted your invitation to join {community}!"
            message2 = f"{receiver_name} is now a member of {community}"
            
            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title2, message=message2, notification_type="Accept", community=community, reference_id=ref)

            instance.delete() # Deletes the invitation after it has been accepted

        if instance.institution:
            institution = instance.institution

            # Lets user know they are now a member
            title = f"You are now a member of {institution}."
            message = f"You now have access to {institution}'s Projects and Notices."
            
            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Accept", institution=institution, reference_id=ref)

            # Send email letting user know they are a member
            # send_membership_email(institution, receiver_, role)

            # Lets sender know their invitation was accepted
            title2 = f"{receiver_name} has accepted your invitation to join {institution}."
            message2 = f"{receiver_name} is now a member of {institution}."
            
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

            title = f"{name} wishes to join {community}"
            message = f"{name} is requesting to join {community}."

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Request", community=community, reference_id=ref)
        if instance.institution:
            institution = instance.institution

            title = f"{name} wishes to join {institution}"
            message = f"{name} is requesting to join {institution}."

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Request", institution=institution, reference_id=ref)


# Send notification when a user's join request has been accepted and they are now part of a community or institution
@receiver(post_save, sender=JoinRequest)
def accept_user_join_request(sender, instance, created, **kwargs):
    if instance.status == 'accepted':
        receiver_ = instance.user_to
        sender_ = instance.user_from
        ref = instance.id
        role = instance.role
        sender_name = check_full_name(sender_)

        if instance.community:
            community = instance.community

            # Message to user requesting to join after request has been approved.
            title = f"You are now a member of {community}"
            message = f"Your request to join {community} has been accepted and you are now a member"

            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title, message=message, notification_type="Accept", community=community, reference_id=ref)
            
            # Message to user accepting the join request letting them know user is now a community member.
            title2 = f"{sender_name} is now a member of {community}"
            message2 = f"{sender_name} is now a member of {community}. They will now have access to {community}'s Projects and Labels"

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title2, message=message2, notification_type="Accept", community=community, reference_id=ref)
            instance.delete() # Deletes the request when it has been accepted

        if instance.institution:
            institution = instance.institution

            # Message to user requesting to join after request has been approved.
            title = f"You are now a member of {institution}"
            message = f"Your request to join {institution} has been accepted and you are now a member"
            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title, message=message, notification_type="Accept", institution=institution, reference_id=ref)

            # Message to user accepting the join request letting them know user is now a institution member.
            title2 = f"{sender_name} is now a member of {institution}"
            message2 = f"{sender_name} is now a member of {institution}. They will now have access to {institution}'s Projects and Notices"

            UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title2, message=message2, notification_type="Accept", institution=institution, reference_id=ref)
            instance.delete() # Deletes the request when it has been accepted

# Sends Site admin notifiation with request to create community
@receiver(post_save, sender=Community)
def community_application(sender, instance, created, **kwargs):
    creator = instance.community_creator
    admin = User.objects.get(email=settings.SITE_ADMIN_EMAIL)

    name = check_full_name(creator)

    title = f"{name} wants to create a community: {instance.community_name}"
    message = f"{name} wants to create a community: {instance.community_name}"

    if created:
        UserNotification.objects.create(to_user=admin, from_user=creator, title=title, message=message, notification_type="Create", community=instance)