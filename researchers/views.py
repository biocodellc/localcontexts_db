from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.utils import is_user_researcher
from projects.utils import add_to_contributors
from helpers.utils import set_notice_defaults

from communities.models import Community
from institutions.models import Institution
from notifications.models import ActionNotification
from helpers.models import ProjectStatus, ProjectComment, Notice
from projects.models import ProjectContributors, Project, ProjectPerson

from projects.forms import CreateProjectForm, ProjectPersonFormset, EditProjectForm
from helpers.forms import ProjectCommentForm

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
                orcid_id = request.POST.get('orcidId')
                orcid_token = request.POST.get('orcidIdToken')
                
                data = form.save(commit=False)
                data.user = request.user
                data.orcid_auth_token = orcid_token
                data.orcid = orcid_id
                data.save()
                return redirect('dashboard')

        return render(request, 'researchers/connect-researcher.html', {'form': form})
    else:
        return redirect('researcher-projects', researcher.id)

@login_required(login_url='login')
def update_researcher(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        if request.method == 'POST':
            update_form = UpdateResearcherForm(request.POST, request.FILES, instance=researcher)

            if update_form.is_valid():
                data = update_form.save(commit=False)
                data.save()

                messages.add_message(request, messages.SUCCESS, 'Updated!')
                return redirect('researcher-update', researcher.id)
        else:
            update_form = UpdateResearcherForm(instance=researcher)
        
        context = {
            'update_form': update_form,
            'researcher': researcher,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/update-researcher.html', context)

@login_required(login_url='login')
def researcher_notices(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        context = {
            'researcher': researcher,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/notices.html', context)


@login_required(login_url='login')
def researcher_projects(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        notices = Notice.objects.filter(placed_by_researcher=researcher)
        form = ProjectCommentForm(request.POST or None)

        if request.method == 'POST':
            notice_id = request.POST.get('notice-id')
            # TODO: Fix this
            # community_id = request.POST.get('community-id')
            # community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if notice_id:
                    notice = Notice.objects.get(id=notice_id)
                    data.notice = notice

                data.sender = request.user
                # data.community = community
                data.save()
                
                return redirect('researcher-projects', researcher.id)

        context = {
            'notices': notices,
            'researcher': researcher,
            'form': form,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        if request.method == "GET":
            form = CreateProjectForm(request.POST or None)
            formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())
        elif request.method == "POST":
            form = CreateProjectForm(request.POST)
            formset = ProjectPersonFormset(request.POST)

            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.project_creator = request.user
                data.save()
                # Add project to researcher projects
                researcher.projects.add(data)

                notices_selected = request.POST.getlist('checkbox-notice')
                if len(notices_selected) > 1:
                    notice = Notice.objects.create(notice_type='biocultural_and_traditional_knowledge', placed_by_researcher=researcher, project=data)
                    set_notice_defaults(notice)
                else:
                    for selected in notices_selected:
                        if selected == 'bcnotice':
                            notice = Notice.objects.create(notice_type='biocultural', placed_by_researcher=researcher, project=data)
                            set_notice_defaults(notice)
                        elif selected == 'tknotice':
                            notice = Notice.objects.create(notice_type='traditional_knowledge', placed_by_researcher=researcher, project=data)
                            set_notice_defaults(notice)

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Get project contributors instance and add researcher to it
                contributors = ProjectContributors.objects.get(project=data)
                contributors.researchers.add(researcher)
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(contributors, data, institutions_selected, researchers_selected)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()

                return redirect('researcher-projects', researcher.id)

        context = {
            'researcher': researcher,
            'form': form,
            'formset': formset,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/create-project.html', context)

@login_required(login_url='login')
def edit_project(request, researcher_id, project_uuid):
    researcher = Researcher.objects.get(id=researcher_id)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        project = Project.objects.get(unique_id=project_uuid)
        form = EditProjectForm(request.POST or None, instance=project)

        if request.method == 'POST':
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
        context = {
            'researcher': researcher, 
            'project': project, 
            'form': form, 
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/edit-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_communities(request, pk, proj_id):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('researcher-restricted', researcher.id)
    else:
        project = Project.objects.get(id=proj_id)
        notice_exists = Notice.objects.filter(project=project).exists()
        communities = Community.objects.all()

        if request.method == "POST":
            # Set private project to discoverable
            if project.project_privacy == 'Private':
                project.project_privacy = 'Discoverable'
                project.save()

            communities_selected = request.POST.getlist('selected_communities')
            message = request.POST.get('notice_message')

            for community_id in communities_selected:
                community = Community.objects.get(id=community_id)
                
            # add community to notice instance
            if notice_exists:
                notices = Notice.objects.filter(project=project)
                notice_status = ProjectStatus.objects.create(community=community, seen=False) # Creates a notice status for each community
                for notice in notices:
                    notice.communities.add(community)
                    notice.save()

                    # Create notice status
                    notice_status.notice = notice
                    notice_status.save()

                    # Create first comment for notice
                    ProjectComment.objects.create(notice=notice, community=community, sender=request.user, message=message)

                    # Create notification
                    reference_id = str(notice.id)
                    title =  "A Notice has been placed by " + str(researcher.user.get_full_name) + '.'
                    ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=reference_id, sender=request.user, title=title)
            
            return redirect('researcher-projects', researcher.id)

        context = {
            'researcher': researcher,
            'project': project,
            'communities': communities,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/notify.html', context)

def restricted_view(request, pk):
    researcher = Researcher.objects.get(id=pk)
    return render(request, 'researchers/restricted.html', {'researcher': researcher})