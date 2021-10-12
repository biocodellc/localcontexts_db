from communities.models import InviteMember, Community
from accounts.models import UserAffiliation

def is_community_in_user_community(user, community):
    u = UserAffiliation.objects.get(user=user)
    community_list = u.communities.all()
    if community in community_list:
        return True
    else:
        return False

def check_member_role_community(user, community):
    u = UserAffiliation.objects.get(user=user)
    community_list = u.communities.all()

    if community in community_list:
        c = Community.objects.get(id=community.id)

        admins = c.get_admins()
        editors = c.get_editors()
        viewers = c.get_viewers()

        if user in admins or user == c.community_creator:
            return 'admin'

        elif user in editors:
            return 'editor'

        elif user in viewers:
            return 'viewer'
    else:
        return False

def does_community_invite_exist(user, community):
    return InviteMember.objects.filter(receiver=user, community=community).exists()

