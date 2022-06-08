from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from helpers.models import Notice, Connections
from projects.models import ProjectContributors, ProjectCreator

register = template.Library()

@register.simple_tag
def researcher_notifications(researcher):
    return ActionNotification.objects.filter(researcher=researcher)

@register.simple_tag
def anchor(url_name, section_id, researcher_id):
    return reverse(url_name, kwargs={'pk': researcher_id}) + "#project-unique-" + str(section_id)

@register.simple_tag
def get_notices_count(researcher):
    return Notice.objects.filter(placed_by_researcher=researcher).count()

@register.simple_tag
def get_labels_count(researcher):
    count = 0
    projects_created_researcher = ProjectCreator.objects.filter(researcher=researcher)
    for instance in projects_created_researcher:
        if instance.project.has_labels():
            count += 1
    return count

@register.simple_tag
def unread_notifications(researcher):
    return ActionNotification.objects.filter(researcher=researcher, viewed=False).exists()

@register.simple_tag
def researcher_contributing_projects(researcher):
    contributors = ProjectContributors.objects.filter(researchers=researcher)
    return contributors

@register.simple_tag
def connections_count(researcher):
    connections = Connections.objects.get(researcher=researcher)
    return connections.communities.count()
