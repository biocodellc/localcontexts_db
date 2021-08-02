from django import template
from django.urls import reverse
from django.templatetags.static import static
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from notifications.models import ActionNotification
from communities.models import JoinRequest, Community
from projects.models import Project, ProjectContributors

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
    return request_exists

@register.simple_tag
def project_has_labels_from_current_community(project_id, community):
    project = Project.objects.get(id=project_id)
    bclabels_exist = project.bclabels.filter(community=community).exists()
    tklabels_exist = project.tklabels.filter(community=community).exists()
    if bclabels_exist or tklabels_exist:
        return True
    else:
        return False

@register.simple_tag
def unread_notifications(community):
    notifications_exist = ActionNotification.objects.filter(community=community, viewed=False).exists()
    return notifications_exist

@register.simple_tag
def community_contributing_projects(community):
    contributors = ProjectContributors.objects.filter(communities=community)
    return contributors

@register.simple_tag
def get_bclabel_img_url(img_type, *args, **kwargs):
    # Returns image url, usage: <img src="{% get_bclabel_img_url img_type %}">
    if img_type == 'bcr':
        image_path = 'images/bc-labels/bc-research-use.png'
    elif img_type =='bccv':
        image_path = 'images/bc-labels/bc-consent-verified.png'
    elif img_type =='bcocoll':
        image_path = 'images/bc-labels/bc-open-to-collaboration.png'
    elif img_type =='bcocomm':
        image_path = 'images/bc-labels/bc-open-to-commercialization.png'
    elif img_type =='bcp':
        image_path = 'images/bc-labels/bc-provenance.png'
    elif img_type =='bcmc':
        image_path = 'images/bc-labels/bc-multiple-community.png'

    return static(image_path)