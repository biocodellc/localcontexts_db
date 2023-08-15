from .models import ActionNotification, UserNotification
from communities.models import Community
from institutions.models import Institution
from researchers.models import Researcher
from accounts.utils import get_users_name

def send_simple_action_notification(sender, target_org, title, notification_type, reference_id):
    target_type_mapping = {
        Community: 'community',
        Institution: 'institution',
        Researcher: 'researcher',
    }

    target_type_key = target_type_mapping.get(type(target_org))
    if target_type_key:
        ActionNotification.objects.create(
            sender=sender,
            notification_type=notification_type,
            title=title,
            reference_id=reference_id,
            **{target_type_key: target_org}
        )


def send_action_notification_to_project_contribs(project): # sent when a new comment is added to a Project
    from projects.models import ProjectContributors

    truncated_project_title = project.title[:30]
    title = f'Project "{truncated_project_title}" has a new comment'
    contrib = ProjectContributors.objects.prefetch_related('communities', 'institutions', 'researchers').get(project=project)

    for attr in ['communities', 'institutions', 'researchers']:
        recipients = getattr(contrib, attr).all()
        for recipient in recipients:
            send_simple_action_notification(None, recipient, title, 'Projects', project.unique_id)


# MEMBER INVITES 
def send_account_member_invite(invite): # Send notification when community or institution sends a member invite to a user
    sender_name = get_users_name(invite.sender)
    entity = invite.community or invite.institution
    entity_type = 'community' if invite.community else 'institution'

    title = f"{sender_name} has invited you to join {entity}."
    message = invite.message or f"You've been invited to join {entity} with the role of {invite.role}"

    UserNotification.objects.create(
        from_user=invite.sender, 
        to_user=invite.receiver, 
        title=title, 
        message=message, 
        notification_type="Invitation", 
        **{entity_type: entity}, 
        reference_id=invite.id, 
        role=invite.role
    )


def send_user_notification_member_invite_accept(member_invite): # Send notification when user accepts a member invite from community or institution
    sender_ = member_invite.sender
    receiver_ = member_invite.receiver
    receiver_name = get_users_name(receiver_)
    entity = member_invite.community or member_invite.institution
    entity_type = 'community' if member_invite.community else 'institution'

    # Lets user know they are now a member
    title = f"You are now a member of {entity}."
    message = f"You now have access to {entity}'s Projects and {'Labels' if entity_type == 'community' else 'Notices' }."
    UserNotification.objects.create(to_user=receiver_, from_user=sender_, title=title, message=message, notification_type="Accept", **{entity_type: entity}, reference_id=member_invite.id)
    
    # Lets sender know their invitation was accepted
    title2 = f"{receiver_name} has accepted your invitation to join {entity}!"
    message2 = f"{receiver_name} is now a member of {entity}"
    UserNotification.objects.create(to_user=sender_, from_user=receiver_, title=title2, message=message2, notification_type="Accept", **{entity_type: entity}, reference_id=member_invite.id)

    member_invite.delete() # Deletes the invitation after it has been accepted


# JOIN REQUESTS
def send_action_notification_join_request(join_request): # Send notification when user wishes to join a community or institution
    sender_name = get_users_name(join_request.user_from)
    entity = join_request.community or join_request.institution
    entity_type = 'community' if join_request.community else 'institution'
    title = f"{sender_name} is requesting to join {entity}"

    ActionNotification.objects.create(title=title, **{entity_type: entity}, sender=join_request.user_from, notification_type="Members", reference_id=join_request.id)
