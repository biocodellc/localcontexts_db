from django import template
from django.urls import reverse
from notifications.models import ActionNotification, NoticeStatus
from bclabels.models import BCNotice
from tklabels.models import TKNotice
from communities.models import JoinRequest
from institutions.models import Institution

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
def get_projects_count(institution_id):
    target_institution = Institution.objects.get(id=institution_id)
    projects_count = target_institution.projects.count()
    return projects_count

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

@register.simple_tag
def bcnotice_status_exists(project, community):
    # Check if bc notice of target project exists
    bcnotice_exists = BCNotice.objects.filter(project=project).exists()

    # If it does, get the notice
    if bcnotice_exists:
        bcnotice = BCNotice.objects.get(project=project)
        # See if this notice has a status with target community
        notice_status_exists = NoticeStatus.objects.filter(bcnotice=bcnotice, community=community).exists()

        if notice_status_exists:
            return True
        else:
            return False
    else:
        return False

@register.simple_tag
def tknotice_status_exists(project, community):
    tknotice_exists = TKNotice.objects.filter(project=project).exists()

    if tknotice_exists:
        tknotice = TKNotice.objects.get(project=project)
        notice_status_exists = NoticeStatus.objects.filter(tknotice=tknotice, community=community).exists()

        if notice_status_exists:
            return True
        else:
            return False
    else:
        return False