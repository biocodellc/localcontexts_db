from communities.models import InviteMember
from accounts.models import UserAffiliation

def is_community_in_user_community(user, community):
    u = UserAffiliation.objects.prefetch_related('communities').get(user=user)
    if community in u.communities.all():
        return True
    else:
        return False

def check_member_role_community(user, community):
    u = UserAffiliation.objects.prefetch_related('communities').get(user=user)

    if community in u.communities.all():
        if user in community.admins.all() or user == community.community_creator:
            return 'admin'

        elif user in community.editors.all():
            return 'editor'

        elif user in community.viewers.all():
            return 'viewer'
    else:
        return False

def does_community_invite_exist(user, community):
    return InviteMember.objects.filter(receiver=user, community=community).exists()

