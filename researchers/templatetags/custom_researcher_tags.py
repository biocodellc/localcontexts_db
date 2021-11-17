from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from helpers.models import Notice, Connections
from projects.models import ProjectContributors

register = template.Library()

@register.simple_tag
def researcher_notifications(researcher):
    notifications = ActionNotification.objects.filter(researcher=researcher)
    return notifications

@register.simple_tag
def anchor(url_name, section_id, researcher_id):
    return reverse(url_name, kwargs={'pk': researcher_id}) + "#project-unique-" + str(section_id)

@register.simple_tag
def get_notices_count(researcher):
    notice_count = Notice.objects.filter(placed_by_researcher=researcher).count()
    return notice_count

@register.simple_tag
def get_labels_count(researcher):
    count = 0
    for project in researcher.projects.all():
        if project.has_labels():
            count += 1
    return count

@register.simple_tag
def unread_notifications(researcher):
    unread_notifications_exist = ActionNotification.objects.filter(researcher=researcher, viewed=False).exists()
    return unread_notifications_exist

@register.simple_tag
def researcher_contributing_projects(researcher):
    contributors = ProjectContributors.objects.filter(researchers=researcher)
    return contributors

@register.simple_tag
def connections_count(researcher):
    connections = Connections.objects.get(researcher=researcher)
    return connections.communities.count()
