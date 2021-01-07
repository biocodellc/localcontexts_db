from communities.models import UserCommunity, InviteMember
from django.contrib.auth.models import Group

def checkif_community_in_user_community(user, community):
    u = UserCommunity.objects.get(user=user)
    community_list = u.communities.all()

    if community in community_list:
        return print('################# USER ALREADY A MEMBER ########################')
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
    
