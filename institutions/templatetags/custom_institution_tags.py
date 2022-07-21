from django import template
from django.urls import reverse
from institutions.models import Institution
from notifications.models import ActionNotification
from helpers.models import Notice, Connections
from projects.models import ProjectContributors, ProjectCreator
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
    return Notice.objects.filter(institution=institution).count()

@register.simple_tag
def get_labels_count(institution):
    count = 0
    projects_created_institution = ProjectCreator.objects.filter(institution=institution)
    for instance in projects_created_institution:
        if instance.project.has_labels():
            count += 1
    return count

@register.simple_tag
def institution_contributing_projects(institution):
    return ProjectContributors.objects.filter(institutions=institution)

@register.simple_tag
def connections_count(institution):
    connections = Connections.objects.get(institution=institution)
    return connections.communities.count()

@register.simple_tag
def connections_projects_with_labels(community, organization):
    # pass instance of researcher or institution

    # get all labels from target community
    bclabels = BCLabel.objects.filter(community=community)
    tklabels = TKLabel.objects.filter(community=community)

    target_projects = []

    for bclabel in bclabels:
        for project in bclabel.project_bclabels.all():
            if isinstance(organization, Institution):
                if ProjectCreator.objects.filter(institution=organization, project=project).exists():
                    org_created_project = ProjectCreator.objects.get(institution=organization, project=project)
                    target_projects.append(org_created_project.project)

            if isinstance(organization, Researcher):
                if ProjectCreator.objects.filter(researcher=organization, project=project).exists():
                    org_created_project = ProjectCreator.objects.get(researcher=organization, project=project)
                    target_projects.append(org_created_project.project)

    for tklabel in tklabels:
        for project in tklabel.project_tklabels.all():

            if isinstance(organization, Institution):
                if ProjectCreator.objects.filter(institution=organization, project=project).exists():
                    org_created_project = ProjectCreator.objects.get(institution=organization, project=project)
                    target_projects.append(org_created_project.project)

            if isinstance(organization, Researcher):
                if ProjectCreator.objects.filter(researcher=organization, project=project).exists():
                    org_created_project = ProjectCreator.objects.get(researcher=organization, project=project)
                    target_projects.append(org_created_project.project)

    projects = set(target_projects)
    return projects

    