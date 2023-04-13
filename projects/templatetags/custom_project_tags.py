from django import template
from institutions.models import Institution
from researchers.models import Researcher
from communities.models import Community
from projects.models import Project, ProjectContributors

register = template.Library()

@register.simple_tag
def source_project_title(uuid):
    try:
        title = Project.objects.filter(unique_id=uuid).values_list('title', flat=True).first()
        return title
    except Project.DoesNotExist:
        return None

@register.simple_tag
def get_all_researchers(researcher_to_exclude):
    if researcher_to_exclude:
        return Researcher.objects.select_related('user').exclude(id=researcher_to_exclude.id)
    else:
        return Researcher.objects.select_related('user').all()

@register.simple_tag
def get_all_institutions(institution_to_exclude):
    if institution_to_exclude:
        return Institution.approved.exclude(id=institution_to_exclude.id)
    else:
        return Institution.approved.all()

@register.simple_tag
def get_all_communities(community_to_exclude):
    if community_to_exclude:
        return Community.approved.exclude(id=community_to_exclude.id)
    else:
        return Community.approved.all()

@register.simple_tag
def define(val=None):
    # To use: {% define 'oldVariable' as newVariable %}
  return val

@register.simple_tag
def connections_collaborative_projects(target_account, collaborating_account):
    projects = Project.objects.none()
    projects_list = []

    if isinstance(target_account, Institution):
        if isinstance(collaborating_account, Institution):
            projects_list = ProjectContributors.objects.filter(institutions=collaborating_account).filter(institutions=target_account).values_list('project__unique_id', flat=True)
        if isinstance(collaborating_account, Community):
            projects_list = target_account.contributing_institutions.filter(communities=collaborating_account).values_list('project__unique_id', flat=True)
        if isinstance(collaborating_account, Researcher):
            projects_list = target_account.contributing_institutions.filter(researchers=collaborating_account).values_list('project__unique_id', flat=True)
    
    if isinstance(target_account, Community):
        if isinstance(collaborating_account, Community):
            projects_list = ProjectContributors.objects.filter(communities=collaborating_account).filter(communities=target_account).values_list('project__unique_id', flat=True)
        if isinstance(collaborating_account, Institution):
            projects_list = target_account.contributing_communities.filter(institutions=collaborating_account).values_list('project__unique_id', flat=True)
        if isinstance(collaborating_account, Researcher):
            projects_list = target_account.contributing_communities.filter(researchers=collaborating_account).values_list('project__unique_id', flat=True)
    
    if isinstance(target_account, Researcher):
        if isinstance(collaborating_account, Researcher):
            projects_list = ProjectContributors.objects.filter(researchers=collaborating_account).filter(researchers=target_account).values_list('project__unique_id', flat=True)
        if isinstance(collaborating_account, Community):
            projects_list = target_account.contributing_researchers.filter(communities=collaborating_account).values_list('project__unique_id', flat=True)
        if isinstance(collaborating_account, Institution):
            projects_list = target_account.contributing_researchers.filter(institutions=collaborating_account).values_list('project__unique_id', flat=True)

    projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=projects_list).order_by('-date_added')
    return projects