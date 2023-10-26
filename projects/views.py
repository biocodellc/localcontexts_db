from django.shortcuts import render, redirect
from .models import Project, ProjectContributors, ProjectCreator
from helpers.models import Notice
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from django.http import Http404
from accounts.models import UserAffiliation
from researchers.models import Researcher
from helpers.downloads import download_project_zip
from localcontexts.utils import dev_prod_or_local
from .utils import can_download_project, return_project_labels_by_community

def view_project(request, unique_id):
    try:
        project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=unique_id)
    except Project.DoesNotExist:
        return render(request, '404.html', status=404)
    
    sub_projects = Project.objects.filter(source_project_uuid=project.unique_id).values_list('unique_id', 'title')
    notices = Notice.objects.filter(project=project, archived=False)
    creator = ProjectCreator.objects.get(project=project)
    communities = None
    institutions = None
    user_researcher = Researcher.objects.none()
    label_groups = return_project_labels_by_community(project)
    can_download = can_download_project(request, creator)

    #  If user is logged in AND belongs to account of a contributor
    if request.user.is_authenticated:
        affiliations = UserAffiliation.objects.get(user=request.user)

        community_ids = ProjectContributors.objects.filter(project=project).values_list('communities__id', flat=True)
        institution_ids = ProjectContributors.objects.filter(project=project).values_list('institutions__id', flat=True)
        communities = affiliations.communities.filter(id__in=community_ids)
        institutions = affiliations.institutions.filter(id__in=institution_ids)

        researcher_ids = ProjectContributors.objects.filter(project=project).values_list('researchers__id', flat=True)

        if Researcher.objects.filter(user=request.user).exists():
            researcher = Researcher.objects.get(user=request.user)
            researchers = Researcher.objects.filter(id__in=researcher_ids)
            if researcher in researchers:
                user_researcher = Researcher.objects.get(id=researcher.id)
    
    template_name = project.get_template_name(request.user)
            
    context = {
        'project': project, 
        'notices': notices,
        'creator': creator,
        'communities': communities,
        'institutions': institutions,
        'user_researcher': user_researcher,
        'sub_projects': sub_projects,
        'template_name': template_name,
        'can_download': can_download,
        'label_groups': label_groups,
    }

    if template_name:
        if project.can_user_access(request.user) == 'partial' or project.can_user_access(request.user) == True:
            return render(request, 'projects/view-project.html', context)
        else:
            return redirect('restricted')
    else:
        return redirect('restricted')


def download_project(request, unique_id):
    try:
        project = Project.objects.get(unique_id=unique_id)
        can_download = can_download_project(request, project.project_creator_project.first())

        if project.project_privacy == "Private" or dev_prod_or_local(request.get_host()) == 'DEV' or not can_download:
            return redirect('restricted')
        else:
            return download_project_zip(project)
    except:
        raise Http404()

def embed_project(request, unique_id):
    layout = request.GET.get('lt')
    lang = request.GET.get('lang')

    project = project = Project.objects.prefetch_related(
                    'bc_labels', 
                    'tk_labels', 
                    'bc_labels__community', 
                    'tk_labels__community',
                    'bc_labels__bclabel_translation', 
                    'tk_labels__tklabel_translation',
                    ).get(unique_id=unique_id)
    notices = Notice.objects.filter(project=project, archived=False)
    label_groups = return_project_labels_by_community(project)
    # tk_labels = TKLabel.objects.filter(project_tklabels=project)
    # bc_labels = BCLabel.objects.filter(project_bclabels=project)
    
    context = {
        'layout' : layout,
        'lang' : lang,
        'notices' : notices,
        'label_groups' :  label_groups,
        'project' : project
    }
    return render(request, 'projects/embed-project.html', context)