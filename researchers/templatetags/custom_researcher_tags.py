from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from helpers.models import ProjectStatus, Notice
from researchers.models import Researcher
from projects.models import ProjectContributors, Project

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
def project_status_exists(project_uuid, community):
    # Check if project exists
    project_exists = Project.objects.filter(unique_id=project_uuid).exists()

    # If it does, get the project
    if project_exists:
        project = Project.objects.get(unique_id=project_uuid)
        # See if this project has a status with target community
        project_status_exists = ProjectStatus.objects.filter(project=project, community=community).exists()

        if project_status_exists:
            return True
        else:
            return False
    else:
        return False

@register.simple_tag
def researcher_contributing_projects(researcher):
    contributors = ProjectContributors.objects.filter(researchers=researcher)
    return contributors