from projects.models import ProjectContributors
from helpers.models import Notice

def get_projects_count(researcher):
    contrib_count = ProjectContributors.objects.filter(researcher=researcher).count()
    return contrib_count

def get_notices_count(researcher):
    notice_count = Notice.objects.filter(placed_by_researcher=researcher).count()
    return notice_count