from django import template
from django.urls import reverse
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from notifications.models import CommunityNotification
from communities.models import CommunityJoinRequest

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
def community_notifications(community):
    notifications = CommunityNotification.objects.filter(community=community)
    return notifications

@register.simple_tag
def join_request(community, user):
    request_exists = CommunityJoinRequest.objects.filter(target_community=community, user_from=user).exists()
    if request_exists:
        return True
    else:
        return False
    