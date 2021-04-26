from projects.models import ProjectContributors
from bclabels.models import BCNotice
from tklabels.models import TKNotice

def get_projects_count(researcher):
    contrib_count = ProjectContributors.objects.filter(researcher=researcher).count()
    return contrib_count

def get_notices_count(researcher):
    bcnotices = BCNotice.objects.filter(placed_by_researcher=researcher).count()
    tknotices = TKNotice.objects.filter(placed_by_researcher=researcher).count()
    return bcnotices + tknotices