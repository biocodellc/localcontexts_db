from django import template
from django.urls import reverse
from django.templatetags.static import static
from institutions.models import Institution
from notifications.models import ActionNotification
from projects.models import Project, ProjectCreator
from helpers.models import EntitiesNotified, Connections
from bclabels.models import BCLabel
from researchers.models import Researcher
from tklabels.models import TKLabel

register = template.Library()

# COUNTERS

# How many total Labels have been applied to projects
@register.simple_tag
def get_label_count(community):
    count = 0
    # Get all labels in this community
    # check to see if label exists in projects

    for label in BCLabel.objects.filter(community=community):
        count = count + label.project_bclabels.count()
    for label in TKLabel.objects.filter(community=community):
        count = count + label.project_tklabels.count()
    return count

# How many Projects has this community been notified of
@register.simple_tag
def community_notified_count(community):
    return EntitiesNotified.objects.prefetch_related('communities').filter(communities=community).count()

# How many connections gave been created (how many unique institutions or researchers have had a Label applied to a project)
@register.simple_tag
def connections_count(community):
    connections = Connections.objects.prefetch_related('researchers', 'institutions').get(community=community)
    return connections.researchers.count() + connections.institutions.count()

# Community Connections page
@register.simple_tag
def connections_organization_projects(community, organization):
    # can pass instance of institution or researcher 

    # get all labels from target community
    bclabels = BCLabel.objects.prefetch_related('project_bclabels').filter(community=community)
    tklabels = TKLabel.objects.prefetch_related('project_tklabels').filter(community=community)

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
        if isinstance(organization, Institution):
            if ProjectCreator.objects.filter(institution=organization, project=project).exists():
                target_projects.append(project)
        if isinstance(organization, Researcher):
            if ProjectCreator.objects.filter(researcher=organization, project=project).exists():
                target_projects.append(project)

    # Removes duplicates from the list
    projects = set(target_projects)
    return projects

@register.simple_tag
def anchor(url_name, section_id, community_id):
    return reverse(url_name, kwargs={'pk': community_id}) + "#project-unique-" + str(section_id)

@register.simple_tag
def community_notifications(community):
    return ActionNotification.objects.filter(community=community)

@register.simple_tag
def unread_notifications(community):
    return ActionNotification.objects.filter(community=community, viewed=False).exists()

@register.simple_tag
def get_bclabel_img_url(img_type, *args, **kwargs):
    # Returns image url, usage: <img loading="lazy" src="{% get_bclabel_img_url img_type %}">
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
    # Returns image url, usage: <img loading="lazy" src="{% get_tklabel_img_url img_type %}">
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
