from django import template
from django.urls import reverse
from communities.views import projects
from notifications.models import ActionNotification
from helpers.models import Notice, Connections
from projects.models import ProjectContributors
from bclabels.models import BCLabel
from tklabels.models import TKLabel

register = template.Library()

@register.simple_tag
def institution_notifications(institution):
    notifications = ActionNotification.objects.filter(institution=institution)
    return notifications

@register.simple_tag
def unread_notifications(institution):
    unread_notifications_exist = ActionNotification.objects.filter(institution=institution, viewed=False).exists()
    return unread_notifications_exist

@register.simple_tag
def anchor(url_name, section_id, institution_id):
    return reverse(url_name, kwargs={'pk': institution_id}) + "#project-unique-" + str(section_id)

@register.simple_tag
def get_notices_count(institution):
    notice_count = Notice.objects.filter(placed_by_institution=institution).count()
    return notice_count

@register.simple_tag
def get_labels_count(institution):
    count = 0
    for project in institution.projects.all():
        if project.has_labels():
            count += 1
    return count

@register.simple_tag
def institution_contributing_projects(institution):
    contributors = ProjectContributors.objects.filter(institutions=institution)
    return contributors

@register.simple_tag
def connections_count(institution):
    connections = Connections.objects.get(institution=institution)
    return connections.communities.count()

@register.simple_tag
def connections_projects_with_labels(community, organization):
    # get all labels from target community
    bclabels = BCLabel.objects.filter(community=community)
    tklabels = TKLabel.objects.filter(community=community)

    target_projects = []
    for bclabel in bclabels:
        for project in bclabel.project_bclabels.all():
            if project in organization.projects.all():
                target_projects.append(project)
    for tklabel in tklabels:
        for project in tklabel.project_tklabels.all():
            if project in organization.projects.all():
                target_projects.append(project)
    
    projects = set(target_projects)
    return projects

    