from accounts.models import UserAffiliation
from .models import Institution

def check_member_role(user, institution):
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