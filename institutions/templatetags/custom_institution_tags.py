from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from helpers.models import ProjectStatus, Notice
from institutions.models import Institution
from projects.models import ProjectContributors

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
        count = project.bc_labels.count() + project.tk_labels.count()
    return count


@register.simple_tag
def institution_contributing_projects(institution):
    contributors = ProjectContributors.objects.filter(institutions=institution)
    return contributors
    