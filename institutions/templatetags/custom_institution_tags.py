from django import template
from django.urls import reverse
from notifications.models import ActionNotification
from bclabels.models import BCNotice
from tklabels.models import TKNotice
from projects.models import ProjectContributors
from communities.models import JoinRequest

register = template.Library()

@register.simple_tag
def institution_notifications(institution):
    notifications = ActionNotification.objects.filter(institution=institution)
    return notifications

@register.simple_tag
def anchor(url_name, section_id, institution_id):
    return reverse(url_name, kwargs={'pk': institution_id}) + "#full-notice-card-" + str(section_id)

@register.simple_tag
def anchor_project(url_name, unique_id, institution_id):
    return reverse(url_name, kwargs={'pk': institution_id}) + "#project-unique-" + str(unique_id)

@register.simple_tag
def get_notices_count(institution):
    bcnotices = BCNotice.objects.filter(placed_by_institution=institution).count()
    tknotices = TKNotice.objects.filter(placed_by_institution=institution).count()
    total = bcnotices + tknotices
    return total

@register.simple_tag
def get_projects_count(institution):
    contrib_count = ProjectContributors.objects.filter(institution=institution).count()
    return contrib_count

@register.simple_tag
def join_request(institution, user):
    request_exists = JoinRequest.objects.filter(institution=institution, user_from=user).exists()
    if request_exists:
        return True
    else:
        return False

@register.simple_tag
def unread_notifications(institution):
    notifications = ActionNotification.objects.filter(institution=institution, viewed=False).exists()
    if notifications:
        return True
    else:
        return False
