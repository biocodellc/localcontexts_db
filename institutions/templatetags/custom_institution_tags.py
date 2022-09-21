from django import template
from itertools import chain
from django.urls import reverse
from institutions.models import Institution
from notifications.models import ActionNotification
from helpers.models import Notice, Connections
from projects.models import Project, ProjectContributors, ProjectCreator
from bclabels.models import BCLabel
from researchers.models import Researcher
from tklabels.models import TKLabel

register = template.Library()

@register.simple_tag
def institution_notifications(institution):
    notifications = ActionNotification.objects.filter(institution=institution)
    return notifications

@register.simple_tag
def unread_notifications(institution):
    return ActionNotification.objects.filter(institution=institution, viewed=False).exists()

@register.simple_tag
def anchor(url_name, section_id, institution_id):
    return reverse(url_name, kwargs={'pk': institution_id}) + "#project-unique-" + str(section_id)

@register.simple_tag
def get_notices_count(institution):
    return Notice.objects.filter(institution=institution, archived=False).count()

@register.simple_tag
def get_labels_count(institution):
    count = 0
    for instance in ProjectCreator.objects.select_related('project').prefetch_related('project__bc_labels', 'project__tk_labels').filter(institution=institution):
        if instance.project.has_labels():
            count += 1

    return count

@register.simple_tag
def institution_contributing_projects(institution):
    return ProjectContributors.objects.select_related('project').filter(institutions=institution)

@register.simple_tag
def connections_count(institution):
    connections = Connections.objects.prefetch_related('communities').get(institution=institution)
    return connections.communities.count()

@register.simple_tag
def connections_projects_with_labels(community, organization):
    # pass instance of researcher or institution
    # in organization created projects check if labels applied by target community

    projects = Project.objects.none()

    if isinstance(organization, Institution):
        projects_list = list(chain(
            organization.institution_created_project.filter(project__bc_labels__community=community).values_list('project__unique_id', flat=True),
            organization.institution_created_project.filter(project__tk_labels__community=community).values_list('project__unique_id', flat=True)
        ))
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=projects_list).order_by('-date_added')

    if isinstance(organization, Researcher):
        projects_list = list(chain(
            organization.researcher_created_project.filter(project__bc_labels__community=community).values_list('project__unique_id', flat=True),
            organization.researcher_created_project.filter(project__tk_labels__community=community).values_list('project__unique_id', flat=True)
        ))
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=projects_list).order_by('-date_added')

    return projects
