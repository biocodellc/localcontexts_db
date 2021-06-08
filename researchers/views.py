from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.utils import is_user_researcher

from bclabels.models import BCNotice
from tklabels.models import TKNotice
from communities.models import Community
from notifications.models import ActionNotification, NoticeStatus, NoticeComment
from projects.models import ProjectContributors, Project
# from projects.forms import CreateProjectForm, ProjectContributorsForm
from projects.forms import CreateProjectForm
from notifications.forms import NoticeCommentForm

from .models import Researcher
from .forms import *
from .utils import *

@login_required(login_url='login')
def connect_researcher(request):
    researcher = is_user_researcher(request.user)
    form = ConnectResearcherForm(request.POST or None)
    
    if researcher == False:
        if request.method == "POST":
            if form.is_valid():
                data = form.save(commit=False)
                data.user = request.user
                orcid_id = request.POST.get('orcidId')
                data.orcid = orcid_id
                data.save()
                return redirect('dashboard')

        return render(request, 'researchers/connect-researcher.html', {'form': form})
    else:
        return redirect('researcher-activity', researcher.id)

@login_required(login_url='login')
def update_researcher(request, pk):
    researcher = Researcher.objects.get(id=pk)

    if request.method == 'POST':
        update_form = UpdateResearcherForm(request.POST, request.FILES, instance=researcher)

        if update_form.is_valid():
            data = update_form.save(commit=False)
            if data.orcid:
                if '-' in data.orcid:
                    data.save()
                else: 
                    data.orcid = '-'.join([data.orcid[i:i+4] for i in range(0, len(data.orcid), 4)])
                    data.save()
            else:
                data.save()

            messages.add_message(request, messages.SUCCESS, 'Updated!')
            return redirect('researcher-update', researcher.id)
    else:
        update_form = UpdateResearcherForm(instance=researcher)
    
    context = {
        'update_form': update_form,
        'researcher': researcher,
    }
    return render(request, 'researchers/update-researcher.html', context)

@login_required(login_url='login')
def researcher_notices(request, pk):
    researcher = Researcher.objects.get(id=pk)

    context = {
        'researcher': researcher,
    }
    return render(request, 'researchers/notices.html', context)

@login_required(login_url='login')
def researcher_activity(request, pk):
    researcher = Researcher.objects.get(id=pk)

    bcnotices = BCNotice.objects.filter(placed_by_researcher=researcher)
    tknotices = TKNotice.objects.filter(placed_by_researcher=researcher)

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
            return redirect('researcher-activity', researcher.id)
    else:
        form = NoticeCommentForm()

    context = {
        'researcher': researcher,
        'bcnotices': bcnotices,
        'tknotices': tknotices,
        'form': form,
    }
    return render(request, 'researchers/activity.html', context)


# TODO: display labels only if they have been approved by community
@login_required(login_url='login')
def researcher_projects(request, pk):
    researcher = Researcher.objects.get(id=pk)

    # contribs = ProjectContributors.objects.filter(researcher=researcher)
    bcnotices = BCNotice.objects.filter(placed_by_researcher=researcher)

    context = {
        'researcher': researcher,
        # 'contribs': contribs,
        'bcnotices': bcnotices,
    }

    return render(request, 'researchers/projects.html', context)


# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    researcher = Researcher.objects.get(id=pk)

    if request.method == "POST":
        form = CreateProjectForm(request.POST or None)
        if form.is_valid():
            data = form.save(commit=False)
            data.project_creator = request.user
            data.save()
            # Add project to researcher projects
            researcher.projects.add(data)

            notices_selected = request.POST.getlist('checkbox-notice')

            for notice in notices_selected:
                if notice == 'bcnotice':
                    bcnotice = BCNotice.objects.create(placed_by_researcher=researcher, project=data)
                if notice == 'tknotice':
                    tknotice = TKNotice.objects.create(placed_by_researcher=researcher, project=data)

            # ProjectContributors.objects.create(project=data, researcher=researcher)
            return redirect('researcher-activity', researcher.id)
    else:
        form = CreateProjectForm()

    context = {
        'researcher': researcher,
        'form': form,
    }
    return render(request, 'researchers/create-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_communities(request, pk, proj_id):
    researcher = Researcher.objects.get(id=pk)

    project = Project.objects.get(id=proj_id)
    # contribs = ProjectContributors.objects.get(project=project, researcher=researcher)

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
                    bcnotice.save()

                    # Create notice status
                    notice_status.bcnotice = bcnotice
                    notice_status.save()

                    # Create first comment for notice
                    NoticeComment.objects.create(bcnotice=bcnotice, community=community, sender=request.user, message=message)

                    # Create notification
                    reference_id = str(bcnotice.unique_id)
                    title =  "A BC Notice has been placed by " + str(researcher.user.get_full_name()) + '.'
                    ActionNotification.objects.create(community=community, notification_type='Activity', reference_id=reference_id, sender=request.user, title=title)

            
            # add community to tknotice instance
            if tknotice_exists:
                tknotices = TKNotice.objects.filter(project=project)
                notice_status = NoticeStatus.objects.create(community=community, seen=False)
                for tknotice in tknotices:
                    tknotice.communities.add(community)
                    tknotice.save()

                    # Create notice status
                    notice_status.tknotice = tknotice
                    notice_status.save()

                    # Create first comment for notice
                    NoticeComment.objects.create(tknotice=tknotice, community=community, sender=request.user, message=message)

                    # Create notification
                    reference_id = str(tknotice.unique_id)
                    title =  "A TK Notice has been placed by " + str(researcher.user.get_full_name()) + '.'
                    ActionNotification.objects.create(community=community, notification_type='Activity', reference_id=reference_id, sender=request.user, title=title)

        
        return redirect('researcher-projects', researcher.id)

    context = {
        'researcher': researcher,
        'project': project,
        # 'contribs': contribs,
        'communities': communities,
    }
    return render(request, 'researchers/notify.html', context)



@login_required(login_url='login')
def researcher_relationships(request, pk):
    researcher = Researcher.objects.get(id=pk)


    return render(request, 'researchers/relationships.html', {'researcher': researcher})
