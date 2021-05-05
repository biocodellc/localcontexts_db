from django import template
from django.urls import reverse
from notifications.models import ResearcherNotification
from bclabels.models import BCNotice
from tklabels.models import TKNotice
from projects.models import ProjectContributors

register = template.Library()

@register.simple_tag
def researcher_notifications(researcher):
    notifications = ResearcherNotification.objects.filter(researcher=researcher)
    return notifications

@register.simple_tag
def anchor(url_name, section_id, researcher_id):
    return reverse(url_name, kwargs={'pk': researcher_id}) + "#full-notice-card-" + str(section_id)

@register.simple_tag
def get_notices_count(researcher):
    bcnotices = BCNotice.objects.filter(placed_by_researcher=researcher).count()
    tknotices = TKNotice.objects.filter(placed_by_researcher=researcher).count()
    total = bcnotices + tknotices
    return total

@register.simple_tag
def get_projects_count(researcher):
    contrib_count = ProjectContributors.objects.filter(researcher=researcher).count()
    return contrib_count