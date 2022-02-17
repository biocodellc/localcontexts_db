from django import template
from institutions.models import Institution
from researchers.models import Researcher
from communities.models import Community
from projects.models import Project, ProjectContributors
from helpers.models import ProjectStatus, ProjectComment

register = template.Library()

@register.simple_tag
def project_comments(project, entity):
    # TODO: pass instance of project and instance of researcher, community or institution
    if isinstance(entity, Community):
        return ProjectComment.objects.select_related('community', 'sender').filter(project=project, community=entity)

@register.simple_tag
def project_comments_all(project):
    return ProjectComment.objects.select_related('community', 'sender').filter(project=project)

@register.simple_tag
def project_status(project):
    return ProjectStatus.objects.select_related('community').filter(project=project)

@register.simple_tag
def get_all_researchers():
    return Researcher.objects.select_related('user').all()

@register.simple_tag
def get_all_institutions():
    return Institution.objects.filter(is_approved=True)

@register.simple_tag
def define(val=None):
    # To use: {% define 'oldVariable' as newVariable %}
  return val

@register.simple_tag
def which_communities_notified(project):
    return ProjectStatus.objects.select_related('community').filter(project=project)

@register.simple_tag
def discoverable_project_view(user, project_uuid):
    project = Project.objects.select_related('project_creator').get(unique_id=project_uuid)
    project_contributors = ProjectContributors.objects.prefetch_related('institutions', 'communities', 'researchers').get(project=project)
    
    if user == project.project_creator:
        return True
    
    elif project.community_projects.all(): # is user a part of the community created project
        for community in project.community_projects.all():
            return community.is_user_in_community(user)
    
    elif project.institution_projects.all(): # is user a part of the institution created project
        for institution in project.institution_projects.all():
            return institution.is_user_in_institution(user)

    elif user.profile.is_researcher:  #is user a researcher and is this researcher a contributor
        for researcher in project_contributors.researchers.all():
            return user == researcher.user

    elif project.project_notified.all(): # is user in notified communities
        for notified in project.project_notified.all():
            for community in notified.communities.all():
                return community.is_user_in_community(user)

    else:
        # is user in contributing institutions
        for institution in project_contributors.institutions.all():
            user_in_institution = institution.is_user_in_institution(user)
            return user_in_institution

        # is user in contributing communities
        for community in project_contributors.communities.all():
            user_in_community = community.is_user_in_community(user)
            return user_in_community