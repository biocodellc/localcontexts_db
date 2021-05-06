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

from projects.forms import CreateProjectForm
from notifications.forms import NoticeCommentForm

from .forms import CreateInstitutionForm, UpdateInstitutionForm
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

# Registry
def institution_registry(request):
    institutions = Institution.objects.all()
    return render(request, 'institutions/institution-registry.html', {'institutions': institutions})

# Update institution
@login_required(login_url='login')
def update_institution(request, pk):
    institution = Institution.objects.get(id=pk)
    
    if request.method == "POST":
        update_form = UpdateInstitutionForm(request.POST, request.FILES, instance=institution)
        if update_form.is_valid():
            update_form.save()
            messages.add_message(request, messages.SUCCESS, 'Updated!')
            return redirect('update-institution', institution.id)
    else:
        update_form = UpdateInstitutionForm(instance=institution)

    context = {
        'institution': institution,
        'update_form': update_form,
    }

    return render(request, 'institutions/update-institution.html', context)

# Notices
@login_required(login_url='login')
def institution_notices(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/notices.html', {'institution': institution,})

# Activity
@login_required(login_url='login')
def institution_activity(request, pk):
    institution = Institution.objects.get(id=pk)
    bcnotices = BCNotice.objects.filter(placed_by_institution=institution)
    tknotices = TKNotice.objects.filter(placed_by_institution=institution)

    if request.method == 'POST':
        project_id = request.POST.get('project-id')
        community_id = request.POST.get('community-id')
        project = Project.objects.get(id=project_id)
        community = Community.objects.get(id=community_id)

        form = NoticeCommentForm(request.POST or None)

        if form.is_valid():
            data = form.save(commit=False)
            data.project = project
            data.sender = request.user
            data.community = community
            data.save()
            return redirect('institution-activity', institution.id)
    else:
        form = NoticeCommentForm()

    context = {
        'institution': institution,
        'bcnotices': bcnotices,
        'tknotices': tknotices,
        'form': form,
    }
    return render(request, 'institutions/activity.html', context)

# Projects
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.get(id=pk)
    contribs = ProjectContributors.objects.filter(institution=institution)

    context = {
        'institution': institution,
        'contribs': contribs,
    }
    return render(request, 'institutions/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    institution = Institution.objects.get(id=pk)

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
    }
    return render(request, 'institutions/create-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_communities(request, pk, proj_id):
    institution = Institution.objects.get(id=pk)
    project = Project.objects.get(id=proj_id)
    contribs = ProjectContributors.objects.get(project=project, institution=institution)

    bcnotice_exists = BCNotice.objects.filter(project=project).exists()
    tknotice_exists = TKNotice.objects.filter(project=project).exists()

    communities = Community.objects.all()

    if request.method == "POST":
        communities_selected = request.POST.getlist('selected_communities')
        message = request.POST.get('notice_message')

        for community_id in communities_selected:
            community = Community.objects.get(id=community_id)
            
            # add community to bcnotice instance
            if bcnotice_exists:
                bcnotices = BCNotice.objects.filter(project=project)
                notice_status = NoticeStatus.objects.create(community=community, seen=False) # Creates a notice status for each community
                for bcnotice in bcnotices:
                    bcnotice.communities.add(community)
                    bcnotice.statuses.add(notice_status)
                    bcnotice.message = message
                    bcnotice.save()

                    # Create notification
                    reference_id = str(bcnotice.unique_id)
                    title =  "A BC Notice has been placed by " + str(institution.institution_name) + '.'
                    CommunityNotification.objects.create(community=community, notification_type='Activity', reference_id=reference_id, sender=request.user, title=title)
            
            # add community to tknotice instance
            if tknotice_exists:
                tknotices = TKNotice.objects.filter(project=project)
                notice_status = NoticeStatus.objects.create(community=community, seen=False)
                for tknotice in tknotices:
                    tknotice.communities.add(community)
                    tknotice.statuses.add(notice_status)
                    tknotice.message = message
                    tknotice.save()

                    # Create notification
                    reference_id = str(tknotice.unique_id)
                    title =  "A TK Notice has been placed by " + str(institution.institution_name) + '.'
                    CommunityNotification.objects.create(community=community, notification_type='Activity', reference_id=reference_id, sender=request.user, title=title)

        
        return redirect('institution-projects', institution.id)

    context = {
        'institution': institution,
        'project': project,
        'contribs': contribs,
        'communities': communities,
    }
    return render(request, 'institutions/notify.html', context)


