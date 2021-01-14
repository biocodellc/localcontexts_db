from communities.models import InviteMember, Community
from accounts.models import UserCommunity
from django.contrib.auth.models import Group

def checkif_community_in_user_community(user, community):
    u = UserCommunity.objects.get(user=user)
    community_list = u.communities.all()

    if community in community_list:
        return print('################# USER ALREADY A MEMBER ########################')
    else:
        return False

def check_member_role(user, community):
    u = UserCommunity.objects.get(user=user)
    community_list = u.communities.all()

    if community in community_list:
        c = Community.objects.get(community_name=community)

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
    else:
        return False

def get_site_admin_email():
    group = Group.objects.get(name="Site Administrator")
    users = group.user_set.all()
    emails = []

    for user in users:
        emails.append(user.email)

    return emails
    
