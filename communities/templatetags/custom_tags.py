from django import template
from django.urls import reverse
from django.templatetags.static import static
from communities.models import Community
from institutions.models import Institution
from notifications.models import ActionNotification
from projects.models import Project, ProjectContributors
from helpers.models import EntitiesNotified, Connections
from bclabels.models import BCLabel
from tklabels.models import TKLabel

register = template.Library()

@register.simple_tag
def get_label_count(community):
    # find all labels of this community that have been applied to projects
    count = 0
    projects = Project.objects.all()
    for project in projects:
        bclabels = project.bc_labels.all()
        tklabels = project.tk_labels.all()
        for bclabel in bclabels:
            if bclabel.community == community:
                count += 1
        for tklabel in tklabels:
            if tklabel.community == community:
                count += 1
    return count

@register.simple_tag
def community_notified_count(community):
    count = 0
    for en in EntitiesNotified.objects.all():
        if community in en.communities.all():
            count += 1
    return count

@register.simple_tag
def anchor(url_name, section_id, community_id):
    return reverse(url_name, kwargs={'pk': community_id}) + "#project-unique-" + str(section_id)

@register.simple_tag
def community_notifications(community):
    notifications = ActionNotification.objects.filter(community=community)
    return notifications

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
    elif img_type =='bccb':
        image_path = 'images/bc-labels/bc-open-to-collaboration.png'
    elif img_type =='bcoc':
        image_path = 'images/bc-labels/bc-open-to-commercialization.png'
    elif img_type =='bcp':
        image_path = 'images/bc-labels/bc-provenance.png'
    elif img_type =='bcmc':
        image_path = 'images/bc-labels/bc-multiple-community.png'

    elif img_type =='bccl':
        image_path = 'images/bc-labels/bc-clan.png'
    elif img_type =='bco':
        image_path = 'images/bc-labels/bc-outreach.png'
    elif img_type =='bccnv':
        image_path = 'images/bc-labels/bc-consent-non-verified.png'
    elif img_type =='bcnc':
        image_path = 'images/bc-labels/bc-non-commercial.png'

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
    elif img_type =='tkoc':
        image_path = 'images/tk-labels/tk-commercial.png'
    elif img_type =='tknc':
        image_path = 'images/tk-labels/tk-non-commercial.png'
    elif img_type =='tkco':
        image_path = 'images/tk-labels/tk-community-use-only.png'
    elif img_type =='tko':
        image_path = 'images/tk-labels/tk-outreach.png'
    elif img_type =='tkcb':
        image_path = 'images/tk-labels/tk-open-to-collaboration.png'
    elif img_type =='tkcr':
        image_path = 'images/tk-labels/tk-creative.png'
    return static(image_path)

@register.simple_tag
def connections_count(community):
    connections = Connections.objects.get(community=community)
    return connections.researchers.count() + connections.institutions.count()

@register.simple_tag
def connections_organization_projects(community, organization):
    # can pass instance of institution or researcher 

    # get all labels from target community
    bclabels = BCLabel.objects.filter(community=community)
    tklabels = TKLabel.objects.filter(community=community)

    # set up a storage of projects to check for these labels
    all_projects = []
    # if project has particular label from these lists, append project
    for bclabel in bclabels:
        for project in bclabel.project_bclabels.all():
            all_projects.append(project)
    for tklabel in tklabels:
        for project in tklabel.project_tklabels.all():
            all_projects.append(project)
    
    # if project is found in target institution projects, append to target list
    target_projects = []
    for project in all_projects:
        if project in organization.projects.all():
            target_projects.append(project)

    # Removes duplicates from the list
    projects = set(target_projects)
    return projects
