from projects.models import ProjectContributors
from helpers.models import Notice
from .models import Researcher

def is_user_researcher(user):
    if Researcher.objects.filter(user=user).exists():
        return Researcher.objects.select_related('user').get(user=user)
    else:
        return False

def get_projects_count(researcher):
    return ProjectContributors.objects.filter(researcher=researcher).count()

def get_notices_count(researcher):
    return Notice.objects.filter(placed_by_researcher=researcher).count()

def checkif_user_researcher(current_researcher, user):
    if Researcher.objects.filter(user=user).exists():
        researcher = Researcher.objects.get(user=user)
        if current_researcher == researcher:
            return True
        else:
            return False
    else:
        return False