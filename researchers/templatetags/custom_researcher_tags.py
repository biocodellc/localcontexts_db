from django import template
from django.urls import reverse
from notifications.models import ActionNotification, NoticeStatus
from bclabels.models import BCNotice
from tklabels.models import TKNotice
from researchers.models import Researcher
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
def get_projects_count(researcher_id):
    researcher = Researcher.objects.get(id=researcher_id)
    project_count = researcher.projects.count()
    return project_count

@register.simple_tag
def unread_notifications(researcher):
    unread_notifications_exist = ActionNotification.objects.filter(researcher=researcher, viewed=False).exists()
    return unread_notifications_exist

@register.simple_tag
def bcnotice_status_exists(project, community):
    # Check if bc notice of target project exists
    bcnotice_exists = BCNotice.objects.filter(project=project).exists()

    # If it does, get the notice
    if bcnotice_exists:
        bcnotice = BCNotice.objects.get(project=project)
        # See if this notice has a status with target community
        notice_status_exists = NoticeStatus.objects.filter(bcnotice=bcnotice, community=community).exists()

        if notice_status_exists:
            return True
        else:
            return False
    else:
        return False

@register.simple_tag
def tknotice_status_exists(project, community):
    tknotice_exists = TKNotice.objects.filter(project=project).exists()

    if tknotice_exists:
        tknotice = TKNotice.objects.get(project=project)
        notice_status_exists = NoticeStatus.objects.filter(tknotice=tknotice, community=community).exists()

        if notice_status_exists:
            return True
        else:
            return False
    else:
        return False

@register.simple_tag
def researcher_contributing_projects(researcher):
    contributors = ProjectContributors.objects.filter(researchers=researcher)
    return contributors