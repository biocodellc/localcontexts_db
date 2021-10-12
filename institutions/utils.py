from accounts.models import UserAffiliation
from .models import Institution
from communities.models import InviteMember

def check_member_role_institution(user, institution):
    u = UserAffiliation.objects.get(user=user)
    institution_list = u.institutions.all()

    if institution in institution_list:
        c = Institution.objects.get(id=institution.id)

        admins = c.get_admins()
        editors = c.get_editors()
        viewers = c.get_viewers()

        if user in admins or user == c.institution_creator:
            return 'admin'

        elif user in editors:
            return 'editor'

        elif user in viewers:
            return 'viewer'
        else:
            print('something went wrong, user does not have a role.')
    else:
        return False

def is_institution_in_user_institutions(user, institution):
    u = UserAffiliation.objects.get(user=user)
    institutions_list = u.institutions.all()
    if institution in institutions_list:
        return True
    else:
        return False

def does_institution_invite_exist(user, institution):
    return InviteMember.objects.filter(receiver=user, institution=institution).exists()