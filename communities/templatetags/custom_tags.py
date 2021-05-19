from django import template
from django.urls import reverse
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from notifications.models import ActionNotification
from communities.models import JoinRequest, Community
from projects.models import Project

register = template.Library()

@register.simple_tag
def get_label_count(community):
    bclabels = BCLabel.objects.filter(community=community).count()
    tklabels = TKLabel.objects.filter(community=community).count()
    total_labels = bclabels + tklabels
    return total_labels

@register.simple_tag
def anchor(url_name, section_id, community_id):
    return reverse(url_name, kwargs={'pk': community_id}) + "#full-notice-card-" + str(section_id)

@register.simple_tag
def anchor_project(url_name, contrib_id, community_id):
    return reverse(url_name, kwargs={'pk': community_id}) + "#full-contrib-card-" + str(contrib_id)

@register.simple_tag
def community_notifications(community):
    notifications = ActionNotification.objects.filter(community=community)
    return notifications

@register.simple_tag
def join_request(community, user):
    request_exists = JoinRequest.objects.filter(community=community, user_from=user).exists()
    if request_exists:
        return True
    else:
        return False

@register.simple_tag
def project_has_labels_from_current_community(project_id, community):
    project = Project.objects.get(id=project_id)
    bclabels_exist = project.bclabels.filter(community=community).exists()
    tklabels_exist = project.tklabels.filter(community=community).exists()
    if bclabels_exist or tklabels_exist:
        return True
    else:
        return False
    