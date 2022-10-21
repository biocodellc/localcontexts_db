from django import template
from institutions.models import Institution
from researchers.models import Researcher
from communities.models import Community
from projects.models import Project, ProjectContributors, ProjectCreator
from helpers.models import ProjectStatus, ProjectComment, Notice

register = template.Library()

@register.simple_tag
def which_account_created_project(project):
    created = ProjectCreator.objects.filter(project=project).values(
            'community__community_name',
            'institution__institution_name',
            'researcher__user__username',           
        )
        
    string = ''
    for x in created:
        if x['community__community_name']:
            string = f'at {x["community__community_name"]} | Community'
        if x['institution__institution_name']:
            string = f'at {x["institution__institution_name"]} | Institution'
        if x['researcher__user__username']:
            string = f' | Researcher'
    return string

@register.simple_tag
def show_project_notices(project):
    return Notice.objects.filter(project=project).values('archived', 'notice_type')

@register.simple_tag
def project_comments(project, community):
    # pass instance of project and instance of community
    if isinstance(community, Community):
        return ProjectComment.objects.select_related('community', 'sender', 'project').filter(project=project, community=community)

@register.simple_tag
def project_status(project):
    return ProjectStatus.objects.select_related('community', 'project').filter(project=project)

@register.simple_tag
def get_all_researchers():
    return Researcher.objects.select_related('user').all()

@register.simple_tag
def get_all_institutions():
    return Institution.approved.all()

@register.simple_tag
def define(val=None):
    # To use: {% define 'oldVariable' as newVariable %}
  return val

@register.simple_tag
def which_communities_notified(project):
    return ProjectStatus.objects.select_related('community').filter(project=project)

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

@register.simple_tag
def discoverable_project_view(user, project_uuid):
    project = Project.objects.select_related('project_creator').get(unique_id=project_uuid)
    project_contributors = ProjectContributors.objects.prefetch_related('institutions', 'communities', 'researchers').get(project=project)
    project_creator_org = ProjectCreator.objects.get(project=project)

    # Initialize boolean with false to check which account created the project
    is_community_created = False
    is_institution_created = False
    is_researcher_created = False

    # Check which account created the project
    if project_creator_org.community:
        is_community_created = True
    if project_creator_org.institution:
        is_institution_created = True
    if project_creator_org.researcher:
        is_researcher_created = True

    if user.is_anonymous:
        return False
    
    elif user == project.project_creator:
        return True
    
    elif is_community_created: # was project created by community
        return project_creator_org.community.is_user_in_community(user) # is user a member of the community
    
    elif is_institution_created: # was project created by institution
        return project_creator_org.institution.is_user_in_institution(user) # is user a member of the institution
    
    elif is_researcher_created: # was project created by researcher
        if Researcher.objects.filter(user=user).exists(): # does this user have a researcher account
            return project_creator_org.researcher == Researcher.objects.get(user=user) # is it the same researcher account as project created by instance

    elif Researcher.objects.filter(user=user):  #is user a researcher and is this researcher a contributor
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