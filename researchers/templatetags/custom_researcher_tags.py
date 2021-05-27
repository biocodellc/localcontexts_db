from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from bclabels.models import BCNotice
from tklabels.models import TKNotice
from projects.models import ProjectContributors

register = template.Library()

@register.simple_tag
def researcher_notifications(researcher):
    notifications = ActionNotification.objects.filter(researcher=researcher)
    return notifications

@register.simple_tag
def anchor(url_name, section_id, researcher_id):
    return reverse(url_name, kwargs={'pk': researcher_id}) + "#full-notice-card-" + str(section_id)

@register.simple_tag
def anchor_project(url_name, unique_id, researcher_id):
    return reverse(url_name, kwargs={'pk': researcher_id}) + "#project-unique-" + str(unique_id)

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

@register.simple_tag
def unread_notifications(researcher):
    notifications = ActionNotification.objects.filter(researcher=researcher, viewed=False).exists()
    if notifications:
        return True
    else:
        return False

@register.simple_tag
def bcnotice_status_exists(researcher, community):
    bcnotices = BCNotice.objects.filter(placed_by_researcher=researcher)
    for bcnotice in bcnotices:
        statuses = bcnotice.statuses.all()
        community_status = statuses.filter(community=community)
        return community_status

@register.simple_tag
def tknotice_status_exists(researcher, community):
    tknotices = TKNotice.objects.filter(placed_by_researcher=researcher)
    for tknotice in tknotices:
        statuses = tknotice.statuses.all()
        community_status = statuses.filter(community=community)
        return community_status