from bclabels.models import BCNotice
from tklabels.models import TKNotice
from projects.models import ProjectContributors

def get_notices_count(institution):
    bcnotices = BCNotice.objects.filter(placed_by_institution=institution).count()
    tknotices = TKNotice.objects.filter(placed_by_institution=institution).count()
    total = bcnotices + tknotices
    return total

def get_projects_count(institution):
    contrib_count = ProjectContributors.objects.filter(institution=institution).count()
    return contrib_count
