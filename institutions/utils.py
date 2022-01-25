from accounts.models import UserAffiliation
from communities.models import InviteMember

def is_institution_in_user_institutions(user, institution):
    u = UserAffiliation.objects.prefetch_related('institutions').get(user=user)
    if institution in u.institutions.all():
        return True
    else:
        return False
        
def check_member_role_institution(user, institution):
    u = UserAffiliation.objects.prefetch_related('institutions').get(user=user)
    institution_list = u.institutions.all()

    if institution in institution_list:
        if user in institution.admins.all() or user == institution.institution_creator:
            return 'admin'

        elif user in institution.editors.all():
            return 'editor'

        elif user in institution.viewers.all():
            return 'viewer'
    else:
        return False

def does_institution_invite_exist(user, institution):
    return InviteMember.objects.filter(receiver=user, institution=institution).exists()