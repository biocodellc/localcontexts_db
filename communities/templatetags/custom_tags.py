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

@register.simple_tag
def get_tklabel_img_url(img_type, *args, **kwargs):
    # Returns image url, usage: <img src="{% get_tklabel_img_url img_type %}">
    if img_type == 'tka':
        image_path = 'images/tk-labels/tk-attribution.png'
    elif img_type =='tkcl':
        image_path = 'images/tk-labels/tk-clan.png'
    elif img_type =='tkf':
        image_path = 'images/tk-labels/tk-family.png'
    elif img_type =='tkmc':
        image_path = 'images/tk-labels/tk-multiple-community.png'
    elif img_type =='tkcv':
        image_path = 'images/tk-labels/tk-community-voice.png'

    elif img_type =='tks':
        image_path = 'images/tk-labels/tk-seasonal.png'
    elif img_type =='tkwg':
        image_path = 'images/tk-labels/tk-women-general.png'
    elif img_type =='tkmg':
        image_path = 'images/tk-labels/tk-men-general.png'
    elif img_type =='tkmr':
        image_path = 'images/tk-labels/tk-men-restricted.png'
    elif img_type =='tkwr':
        image_path = 'images/tk-labels/tk-women-restricted.png'
    elif img_type =='tkcs':
        image_path = 'images/tk-labels/tk-culturally-sensitive.png'
    elif img_type =='tkss':
        image_path = 'images/tk-labels/tk-secret-sacred.png'

    elif img_type =='tkv':
        image_path = 'images/tk-labels/tk-verified.png'
    elif img_type =='tknv':
        image_path = 'images/tk-labels/tk-non-verified.png'
    elif img_type =='tkc':
        image_path = 'images/tk-labels/tk-commercial.png'
    elif img_type =='tknc':
        image_path = 'images/tk-labels/tk-non-commercial.png'
    elif img_type =='tkco':
        image_path = 'images/tk-labels/tk-community-use-only.png'
    elif img_type =='tko':
        image_path = 'images/tk-labels/tk-outreach.png'

    return static(image_path)