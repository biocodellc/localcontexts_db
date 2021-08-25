from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from helpers.models import NoticeStatus, Notice
from researchers.models import Researcher
from projects.models import ProjectContributors

register = template.Library()

@register.simple_tag
def researcher_notifications(researcher):
    notifications = ActionNotification.objects.filter(researcher=researcher)
    return notifications

@register.simple_tag
def anchor(url_name, section_id, researcher_id):
    return reverse(url_name, kwargs={'pk': researcher_id}) + "project-unique-" + str(section_id)

@register.simple_tag
def get_notices_count(researcher):
    notice_count = Notice.objects.filter(placed_by_researcher=researcher).count()
    return notice_count

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
def notice_status_exists(project, community):
    # Check if bc notice of target project exists
    notice_exists = Notice.objects.filter(project=project).exists()

    # If it does, get the notice
    if notice_exists:
        notice = Notice.objects.get(project=project)
        # See if this notice has a status with target community
        notice_status_exists = NoticeStatus.objects.filter(notice=notice, community=community).exists()

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