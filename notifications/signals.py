from django.db.models.signals import post_save
from django.dispatch import receiver
from communities.models import *
from .models import *
from accounts.utils import get_users_name

# When the instance of invite member form is saved, send target user a notification
@receiver(post_save, sender=InviteMember)
def send_community_invite(sender, instance, created, **kwargs):
    if instance.status == 'sent':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role
        ref = instance.id
        msg = instance.message
        name = get_users_name(sender_)

        if instance.community:
            community = instance.community
            title = f"{name} has invited you to join {community}."

            if msg:
                message = msg
            else:
                message= f"You've been invited to join {community} with the role of {role}"
            UserNotification.objects.create(from_user=sender_, to_user=receiver_, title=title, message=message, notification_type="Invitation", community=community, reference_id=ref, role=role)

        if instance.institution:
            institution = instance.institution
            title = f"{name} has invited you to join {institution}."

            if msg:
                message = msg
            else:
                message= f"You've been invited to join {institution} with the role of {role}."
            UserNotification.objects.create(from_user=sender_, to_user=receiver_, title=title, message=message, notification_type="Invitation", institution=institution, reference_id=ref, role=role)


# When an invitation to a community or institution is accepted, send target a notification
@receiver(post_save, sender=InviteMember)
def accept_community_invite(sender, instance, **kwargs):
    if instance.status == 'accepted':
        sender_ = instance.sender
        receiver_ = instance.receiver
        role = instance.role
        ref = instance.id
        receiver_name = get_users_name(receiver_)

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

            # Lets sender know their invitation was accepted
            title2 = f"{receiver_name} has accepted your invitation to join {institution}."
            message2 = f"{receiver_name} is now a member of {institution}."
            
            UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title2, message=message2, notification_type="Accept", institution=institution, reference_id=ref)

            instance.delete() # Deletes the invitation after it has been accepted


# Send notification when user wishes to join a community or institution
@receiver(post_save, sender=JoinRequest)
def send_user_join_request(sender, instance, created, **kwargs):
    if created:
        sender_ = instance.user_from
        ref = instance.id
        name = get_users_name(sender_)

        if instance.community:
            community = instance.community

            title = f"{name} wishes to join {community}"
            # message = f"{name} is requesting to join {community}."

            ActionNotification.objects.create(title=title, community=community, sender=sender_, notification_type="Members", reference_id=ref)
        if instance.institution:
            institution = instance.institution

            title = f"{name} wishes to join {institution}"
            # message = f"{name} is requesting to join {institution}."

            ActionNotification.objects.create(title=title, institution=institution, sender=sender_, notification_type="Members", reference_id=ref)
