from projects.models import ProjectContributors
from helpers.models import Notice
from .models import Researcher

def get_projects_count(researcher):
    contrib_count = ProjectContributors.objects.filter(researcher=researcher).count()
    return contrib_count

def get_notices_count(researcher):
    notice_count = Notice.objects.filter(placed_by_researcher=researcher).count()
    return notice_count

def checkif_user_researcher(current_researcher, user):
    user_is_researcher = Researcher.objects.filter(user=user).exists()
    if user_is_researcher:
        researcher = Researcher.objects.get(user=user)
        if current_researcher == researcher:
            return True
        else:
            return False
    else:
        return False