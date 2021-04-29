from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Institution
from researchers.models import Researcher
from projects.models import Project, ProjectContributors
from bclabels.models import BCNotice, NoticeStatus
from tklabels.models import TKNotice
from communities.models import Community
from notifications.models import CommunityNotification

from projects.forms import CreateProjectForm, ProjectCommentForm

from .forms import CreateInstitutionForm, UpdateInstitutionForm
from .utils import *
# from bclabels.forms import AddBCNoticeMessage
# from tklabels.forms import AddTKNoticeMessage

@login_required(login_url='login')
def connect_institution(request):
    return render(request, 'institutions/connect-institution.html')

@login_required(login_url='login')
def create_institution(request):
    if request.method == 'POST':
        form = CreateInstitutionForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.institution_creator = request.user
            data.save()
            return redirect('dashboard')
    else:
        form = CreateInstitutionForm()
        return render(request, 'institutions/create-institution.html', {'form': form})

@login_required(login_url='login')
def institution_registry(request):
    institutions = Institution.objects.all()
    return render(request, 'institutions/institution-registry.html', {'institutions': institutions})

# Dashboard
@login_required(login_url='login')
def institution_dashboard(request, pk):
    institution = Institution.objects.get(id=pk)
    total_notices = get_notices_count(institution)
    total_projects = get_projects_count(institution)
    context = {
        'institution': institution, 
        'total_notices': total_notices,
        'total_projects': total_projects, 
    }
    return render(request, 'institutions/dashboard.html', context)

# Update institution
@login_required(login_url='login')
def update_institution(request, pk):
    institution = Institution.objects.get(id=pk)
    total_notices = get_notices_count(institution)
    total_projects = get_projects_count(institution)

    update_form = UpdateInstitutionForm(instance=institution)
    
    if request.method == "POST":
        update_form = UpdateInstitutionForm(request.POST, instance=institution)
        if update_form.is_valid():
            update_form.save()
            messages.add_message(request, messages.SUCCESS, 'Updated!')
        else:
            update_form = UpdateInstitutionForm(instance=institution)
    context = {
        'institution': institution,
        'update_form': update_form,
        'total_notices': total_notices,
        'total_projects': total_projects,
    }

    return render(request, 'institutions/update-institution.html', context)

# Notices
@login_required(login_url='login')
def institution_notices(request, pk):
    institution = Institution.objects.get(id=pk)
    total_notices = get_notices_count(institution)
    total_projects = get_projects_count(institution)
    context = {
        'institution': institution, 
        'total_notices': total_notices,
        'total_projects': total_projects,
    }
    return render(request, 'institutions/notices.html', context)

# Activity
@login_required(login_url='login')
def institution_activity(request, pk):
    institution = Institution.objects.get(id=pk)
    bcnotices = BCNotice.objects.filter(placed_by_institution=institution)
    tknotices = TKNotice.objects.filter(placed_by_institution=institution)
    total_notices = bcnotices.count() + tknotices.count()
    total_projects = get_projects_count(institution)

    if request.method == 'POST':
        project_id = request.POST.get('project-id')
        community_id = request.POST.get('community-id')
        project = Project.objects.get(id=project_id)
        community = Community.objects.get(id=community_id)

        form = ProjectCommentForm(request.POST or None)

        if form.is_valid():
            data = form.save(commit=False)
            data.project = project
            data.sender = request.user
            data.community = community
            data.save()
            return redirect('institution-activity', institution.id)
    else:
        form = ProjectCommentForm()

    context = {
        'institution': institution,
        'bcnotices': bcnotices,
        'tknotices': tknotices,
        'total_notices': total_notices,
        'total_projects': total_projects,
        'form': form,
    }
    return render(request, 'institutions/activity.html', context)

# Projects
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.get(id=pk)
    total_notices = get_notices_count(institution)
    total_projects = get_projects_count(institution)
    contribs = ProjectContributors.objects.filter(institution=institution)

    context = {
        'institution': institution,
        'contribs': contribs,
        'total_notices': total_notices,
        'total_projects': total_projects,
    }
    return render(request, 'institutions/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    institution = Institution.objects.get(id=pk)
    total_notices = get_notices_count(institution)
    total_projects = get_projects_count(institution)

    if request.method == "POST":
        form = CreateProjectForm(request.POST or None)
        if form.is_valid():
            data = form.save(commit=False)
            data.project_creator = request.user
            data.save()

            notices_selected = request.POST.getlist('checkbox-notice')

            for notice in notices_selected:
                if notice == 'bcnotice':
                    bcnotice = BCNotice.objects.create(placed_by_institution=institution, project=data)
                if notice == 'tknotice':
                    tknotice = TKNotice.objects.create(placed_by_institution=institution, project=data)

            ProjectContributors.objects.create(project=data, institution=institution)
            return redirect('institution-activity', institution.id)
    else:
        form = CreateProjectForm()

    context = {
        'institution': institution,
        'form': form,
        'total_notices': total_notices,
        'total_projects': total_projects,
    }
    return render(request, 'institutions/create-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_communities(request, pk, proj_id):
    institution = Institution.objects.get(id=pk)
    project = Project.objects.get(id=proj_id)
    contribs = ProjectContributors.objects.get(project=project, institution=institution)
    total_notices = get_notices_count(institution)
    total_projects = get_projects_count(institution)

    bcnotice_exists = BCNotice.objects.filter(project=project).exists()
    tknotice_exists = TKNotice.objects.filter(project=project).exists()

    communities = Community.objects.all()

    if request.method == "POST":
        communities_selected = request.POST.getlist('selected_communities')
        message = request.POST.get('notice_message')

        for community_id in communities_selected:
            title = str(institution.institution_name) + " has placed a Notice"

            community = Community.objects.get(id=community_id)

            # Create notification
            CommunityNotification.objects.create(community=community, notification_type='Requests', sender=request.user, title=title)
            
            # add community to bcnotice instance
            if bcnotice_exists:
                bcnotices = BCNotice.objects.filter(project=project)
                notice_status = NoticeStatus.objects.create(community=community, seen=False) # Creates a notice status for each community
                for bcnotice in bcnotices:
                    bcnotice.communities.add(community)
                    bcnotice.statuses.add(notice_status)
                    bcnotice.message = message
                    bcnotice.save()
            
            # add community to tknotice instance
            if tknotice_exists:
                tknotices = TKNotice.objects.filter(project=project)
                notice_status = NoticeStatus.objects.create(community=community, seen=False)
                for tknotice in tknotices:
                    tknotice.communities.add(community)
                    tknotice.statuses.add(notice_status)
                    tknotice.message = message
                    tknotice.save()
        
        return redirect('institution-projects', institution.id)

    context = {
        'institution': institution,
        'project': project,
        'contribs': contribs,
        'communities': communities,
        'total_notices': total_notices,
        'total_projects': total_projects,
    }
    return render(request, 'institutions/notify.html', context)


