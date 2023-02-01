from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from helpers.models import Notice
from projects.models import ProjectContributors, ProjectCreator
from itertools import chain

register = template.Library()

@register.simple_tag
def researcher_notifications(researcher):
    return ActionNotification.objects.filter(researcher=researcher)

# @register.simple_tag
# def anchor(url_name, section_id, researcher_id):
#     return reverse(url_name, kwargs={'pk': researcher_id}) + "#project-unique-" + str(section_id)

@register.simple_tag
def get_notices_count(researcher):
    return Notice.objects.filter(researcher=researcher).count()

@register.simple_tag
def get_labels_count(researcher):
    count = 0
    for instance in ProjectCreator.objects.select_related('project').prefetch_related('project__bc_labels', 'project__tk_labels').filter(researcher=researcher):
        if instance.project.has_labels():
            count += 1
    return count

@register.simple_tag
def unread_notifications(researcher):
    return ActionNotification.objects.filter(researcher=researcher, viewed=False).exists()

@register.simple_tag
def researcher_contributing_projects(researcher):
    return ProjectContributors.objects.select_related('project').filter(researchers=researcher)

@register.simple_tag
def connections_count(researcher):
    contributor_ids = researcher.contributing_researchers.exclude(communities__id=None).values_list('communities__id', flat=True)
    return len(contributor_ids)
