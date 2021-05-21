from communities.models import InviteMember, Community
from accounts.models import UserAffiliation
from django.contrib.auth.models import Group
from bclabels.models import BCLabel
from tklabels.models import TKLabel

def checkif_community_in_user_community(user, community):
    u = UserAffiliation.objects.get(user=user)
    community_list = u.communities.all()

    if community in community_list:
        print('################# USER ALREADY A MEMBER ########################')
        return True
    else:
        return False

def check_member_role(user, community):
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
            print('something went wrong, user does not have a role.')
    else:
        return False

def checkif_invite_exists(user, community):
    invite = InviteMember.objects.filter(receiver=user, community=community).exists()

    if invite:
        print(" #########   INVITATION ALREADY EXISTS  ######### ")
        return True
    else:
        return False   
