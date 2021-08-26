from django import template
from institutions.models import Institution
from researchers.models import Researcher
from communities.models import Community
from helpers.models import NoticeStatus, Notice
from projects.models import Project

register = template.Library()

@register.simple_tag
def get_all_researchers():
    return Researcher.objects.all()

@register.simple_tag
def get_all_institutions():
    return Institution.objects.all()

@register.simple_tag
def define(val=None):
    # To use: {% define 'oldVariable' as newVariable %}
  return val

@register.simple_tag
def which_communities_notified(project):
    if project.project_notice.all().exists():
        notices = Notice.objects.filter(project=project)
        for notice in notices:
            statuses = NoticeStatus.objects.filter(notice=notice)
            return statuses

@register.simple_tag
def discoverable_project_view(user, project_uuid):
    project = Project.objects.get(unique_id=project_uuid)
    contributing_institutions = project.project_contributors.institutions.all()
    contributing_communities = project.project_contributors.communities.all()
    contributing_researchers = project.project_contributors.researchers.all()
    
    if user == project.project_creator:
        return True
    
    elif project.community_projects.all(): # is user a part of the community created project
        for community in project.community_projects.all():
            return community.is_user_in_community(user)
    
    elif project.institution_projects.all(): # is user a part of the institution created project
        for institution in project.institution_projects.all():
            return institution.is_user_in_institution(user)

    elif user.profile.is_researcher:  #is user a researcher and is this researcher a contributor
        for researcher in contributing_researchers:
            return user == researcher.user

    elif project.project_notice.all(): # is user in notified communities
        for notice in project.project_notice.all():
            for community in notice.communities.all():
                return community.is_user_in_community(user)

    else:
        # is user in contributing institutions
        for institution in contributing_institutions:
            user_in_institution = institution.is_user_in_institution(user)
            return user_in_institution

        # is user in contributing communities
        for community in contributing_communities:
            user_in_community = community.is_user_in_community(user)
            return user_in_community