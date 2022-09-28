from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator
from itertools import chain

from localcontexts.utils import dev_prod_or_local
from projects.utils import add_to_contributors
from helpers.utils import *
from accounts.utils import get_users_name

from communities.models import Community
from notifications.models import ActionNotification
from helpers.models import OpenToCollaborateNoticeURL, ProjectStatus, ProjectComment, Notice, EntitiesNotified, Connections
from projects.models import ProjectContributors, Project, ProjectPerson, ProjectCreator

from projects.forms import *
from helpers.forms import ProjectCommentForm, OpenToCollaborateNoticeURLForm
from accounts.forms import ContactOrganizationForm

from helpers.emails import *

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

                # Mark current user as researcher
                request.user.user_profile.is_researcher = True
                request.user.user_profile.save()

                # Send support an email in prod only about a Researcher signing up
                if dev_prod_or_local(request.get_host()) == 'PROD':
                    send_email_to_support(data)
                    
                return redirect('dashboard')

        return render(request, 'researchers/connect-researcher.html', {'form': form})
    else:
        return redirect('researcher-notices', researcher.id)

def public_researcher_view(request, pk):
    try:
        researcher = Researcher.objects.get(id=pk)
        created_projects = ProjectCreator.objects.filter(researcher=researcher)

        # Do notices exist
        bcnotice = False
        tknotice = False
        attrnotice = False
        if Notice.objects.filter(researcher=researcher, notice_type='biocultural').exists():
            bcnotice = True
        if Notice.objects.filter(researcher=researcher, notice_type='traditional_knowledge').exists():
            tknotice = True
        if Notice.objects.filter(researcher=researcher, notice_type='attribution_incomplete').exists():
            attrnotice = True

        projects = []

        for p in created_projects:
            if p.project.project_privacy == 'Public':
                projects.append(p.project)
        
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(researcher=researcher)

        if request.user.is_authenticated:
            form = ContactOrganizationForm(request.POST or None)

            if request.method == 'POST':
                # contact researcher
                if form.is_valid():
                    to_email = ''
                    from_name = form.cleaned_data['name']
                    from_email = form.cleaned_data['email']
                    message = form.cleaned_data['message']
                    to_email = researcher.contact_email

                    send_contact_email(to_email, from_name, from_email, message)
                    messages.add_message(request, messages.SUCCESS, 'Sent!')
                    return redirect('public-researcher', researcher.id)
            else:
                context = { 
                    'researcher': researcher,
                    'projects' : projects,
                    'form': form,
                    'bcnotice': bcnotice,
                    'tknotice': tknotice,
                    'attrnotice': attrnotice,
                    'otc_notices': otc_notices,
                }
                return render(request, 'public.html', context)

        context = { 
            'researcher': researcher,
            'projects' : projects,
            'bcnotice': bcnotice,
            'tknotice': tknotice,
            'attrnotice': attrnotice,
            'otc_notices': otc_notices,
        }
        return render(request, 'public.html', context)
    except:
        raise Http404()


@login_required(login_url='login')
def connect_orcid(request):
    researcher = Researcher.objects.get(user=request.user)
    return redirect('update-researcher', researcher.id)

@login_required(login_url='login')
def disconnect_orcid(request):
    researcher = Researcher.objects.get(user=request.user)
    researcher.orcid = ''
    researcher.orcid_auth_token = ''
    researcher.save()
    return redirect('update-researcher', researcher.id)

@login_required(login_url='login')
def update_researcher(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        if request.method == 'POST':
            update_form = UpdateResearcherForm(request.POST, request.FILES, instance=researcher)

            if update_form.is_valid():
                data = update_form.save(commit=False)
                data.save()

                if not researcher.orcid:
                    orcid_id = request.POST.get('orcidId')
                    orcid_token = request.POST.get('orcidIdToken')
                    researcher.orcid_auth_token = orcid_token
                    researcher.orcid = orcid_id
                    researcher.save()

                messages.add_message(request, messages.SUCCESS, 'Updated!')
                return redirect('update-researcher', researcher.id)
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
        return redirect('public-researcher', researcher.id)
    else:
        urls = OpenToCollaborateNoticeURL.objects.filter(researcher=researcher).values_list('url', 'name')
        form = OpenToCollaborateNoticeURLForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                data = form.save(commit=False)
                data.researcher = researcher
                data.save()
            return redirect('researcher-notices', researcher.id)

        context = {
            'researcher': researcher,
            'user_can_view': user_can_view,
            'form': form,
            'urls': urls,
        }
        return render(request, 'researchers/notices.html', context)


@login_required(login_url='login')
def researcher_projects(request, pk):
    researcher = Researcher.objects.prefetch_related('user').get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        # researcher projects + 
        # projects researcher has been notified of + 
        # projects where researcher is contributor

        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__id', flat=True), 
            researcher.researchers_notified.all().values_list('project__id', flat=True), 
            researcher.contributing_researchers.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids).order_by('-date_added')
        
        p = Paginator(projects, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)
        
        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')
            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if request.POST.get('message'):
                if form.is_valid():
                    data = form.save(commit=False)

                    if project_uuid:
                        project = Project.objects.get(unique_id=project_uuid)
                        data.project = project

                    data.sender = request.user
                    data.community = community
                    data.save()
                    
                    return redirect('researcher-projects', researcher.id)
            else:
                return redirect('researcher-projects', researcher.id)

        context = {
            'projects': projects,
            'researcher': researcher,
            'form': form,
            'user_can_view': user_can_view,
            'items': page,
        }
        return render(request, 'researchers/projects.html', context)

@login_required(login_url='login')
def projects_with_labels(request, pk):
    researcher = Researcher.objects.prefetch_related('user').get(id=pk)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:

        # 1. researcher projects + 
        # 2. projects researcher has been notified of 
        # 3. projects where researcher is contributor

        projects_list = []

        for p in researcher.researcher_created_project.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if p.project.has_labels():
                projects_list.append(p.project)

        for n in researcher.researchers_notified.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if n.project.has_labels():
                projects_list.append(n.project)

        for c in researcher.contributing_researchers.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if c.project.has_labels():
                projects_list.append(c.project)

        projects = list(set(projects_list))

        p = Paginator(projects, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)

        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')
            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if request.POST.get('message'):
                if form.is_valid():
                    data = form.save(commit=False)

                    if project_uuid:
                        project = Project.objects.get(unique_id=project_uuid)
                        data.project = project

                    data.sender = request.user
                    data.community = community
                    data.save()
                    return redirect('researcher-projects-labels', researcher.id)
            else:
                return redirect('researcher-projects-labels', researcher.id)

        context = {
            'projects': projects,
            'researcher': researcher,
            'form': form,
            'user_can_view': user_can_view,
            'items': page,
        }
        return render(request, 'researchers/projects.html', context)

@login_required(login_url='login')
def projects_with_notices(request, pk):
    researcher = Researcher.objects.prefetch_related('user').get(id=pk)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        # 1. researcher projects + 
        # 2. projects researcher has been notified of 
        # 3. projects where researcher is contributor

        projects_list = []

        for p in researcher.researcher_created_project.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if p.project.has_notice():
                projects_list.append(p.project)

        for n in researcher.researchers_notified.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if n.project.has_notice():
                projects_list.append(n.project)

        for c in researcher.contributing_researchers.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if c.project.has_notice():
                projects_list.append(c.project)

        projects = list(set(projects_list))

        p = Paginator(projects, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)

        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')
            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if request.POST.get('message'):
                if form.is_valid():
                    data = form.save(commit=False)

                    if project_uuid:
                        project = Project.objects.get(unique_id=project_uuid)
                        data.project = project

                    data.sender = request.user
                    data.community = community
                    data.save()
                    return redirect('researcher-projects-notices', researcher.id)
            else:
                return redirect('researcher-projects-notices', researcher.id)

        context = {
            'projects': projects,
            'researcher': researcher,
            'form': form,
            'user_can_view': user_can_view,
            'items': page,
        }
        return render(request, 'researchers/projects.html', context)


@login_required(login_url='login')
def projects_creator(request, pk):
    researcher = Researcher.objects.prefetch_related('user').get(id=pk)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        created_projects = researcher.researcher_created_project.all().values_list('project__id', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=created_projects).order_by('-date_added')

        p = Paginator(projects, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        form = ProjectCommentForm(request.POST or None)

        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')
            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if request.POST.get('message'):
                if form.is_valid():
                    data = form.save(commit=False)

                    if project_uuid:
                        project = Project.objects.get(unique_id=project_uuid)
                        data.project = project

                    data.sender = request.user
                    data.community = community
                    data.save()
                    return redirect('researcher-projects-creator', researcher.id)
            else:
                return redirect('researcher-projects-creator', researcher.id)

        context = {
            'projects': projects,
            'researcher': researcher,
            'form': form,
            'user_can_view': user_can_view,
            'items': page,
        }
        return render(request, 'researchers/projects.html', context)

@login_required(login_url='login')
def projects_contributor(request, pk):
    researcher = Researcher.objects.prefetch_related('user').get(id=pk)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        # Get IDs of projects created by researcher and IDs of projects contributed, then exclude the created ones in the project call
        created_projects = researcher.researcher_created_project.all().values_list('project__id', flat=True)
        contrib = researcher.contributing_researchers.all().values_list('project__id', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=contrib).exclude(id__in=created_projects).order_by('-date_added')


        p = Paginator(projects, 5)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        form = ProjectCommentForm(request.POST or None)

        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')
            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if request.POST.get('message'):
                if form.is_valid():
                    data = form.save(commit=False)

                    if project_uuid:
                        project = Project.objects.get(unique_id=project_uuid)
                        data.project = project

                    data.sender = request.user
                    data.community = community
                    data.save()
                    return redirect('researcher-projects-contributor', researcher.id)
            else:
                return redirect('researcher-projects-contributor', researcher.id)

        context = {
            'projects': projects,
            'researcher': researcher,
            'form': form,
            'user_can_view': user_can_view,
            'items': page,
        }
        return render(request, 'researchers/projects.html', context)



# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
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

                # Define project_page field
                domain = request.get_host()
                if 'localhost' in domain:
                    data.project_page = f'http://{domain}/projects/{data.unique_id}'
                else:
                    data.project_page = f'https://{domain}/projects/{data.unique_id}'
                data.save()

                # Add project to researcher projects
                creator = ProjectCreator.objects.select_related('researcher').get(project=data)
                creator.researcher = researcher
                creator.save()

                 # Get a project contributor object and add researcher to it.
                contributors = ProjectContributors.objects.prefetch_related('researchers').get(project=data)
                contributors.researchers.add(researcher)

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                create_notices(notices_selected, researcher, data, None)

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Get project contributors instance and add researcher to it
                contributors = ProjectContributors.objects.get(project=data)
                contributors.researchers.add(researcher)
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id)
                
                # Send notification
                title = 'Your project has been created, remember to notify a community of your project.'
                ActionNotification.objects.create(title=title, sender=request.user, notification_type='Projects', researcher=researcher, reference_id=data.unique_id)

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
        return redirect('restricted')
    else:
        project = Project.objects.get(unique_id=project_uuid)
        form = EditProjectForm(request.POST or None, instance=project)
        formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
        contributors = ProjectContributors.objects.get(project=project)
        notices = Notice.objects.none()

        # Check to see if notice exists for this project and pass to template
        if Notice.objects.filter(project=project).exists():
            notices = Notice.objects.filter(project=project)

        if request.method == 'POST':
            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.save()

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)
            
                # Which notices were selected to change
                notices_selected = request.POST.getlist('checkbox-notice')
                create_notices(notices_selected, researcher, data, notices)

            return redirect('researcher-projects', researcher.id)    

        context = {
            'researcher': researcher, 
            'project': project, 
            'notices': notices,
            'form': form, 
            'formset': formset,
            'contributors': contributors,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/edit-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_others(request, pk, proj_id):
    researcher = Researcher.objects.select_related('user').get(id=pk)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        project = Project.objects.prefetch_related('bc_labels', 'tk_labels', 'project_status').get(id=proj_id)
        entities_notified = EntitiesNotified.objects.prefetch_related('communities').get(project=project)
        communities = Community.approved.all()

        if request.method == "POST":
            # Set private project to discoverable
            if project.project_privacy == 'Private':
                project.project_privacy = 'Discoverable'
                project.save()

            communities_selected = request.POST.getlist('selected_communities')

            message = request.POST.get('notice_message')

            # Reference ID and title for notification
            reference_id = str(project.unique_id)
            name = get_users_name(researcher.user)
            title =  f'{name} has notified you of a Project.'

            for community_id in communities_selected:
                # Add each selected community to notify entities instance
                community = Community.objects.get(id=community_id)
                entities_notified.communities.add(community)

                # Create project status, first comment and  notification
                ProjectStatus.objects.create(project=project, community=community, seen=False)
                if message:
                    ProjectComment.objects.create(project=project, community=community, sender=request.user, message=message)
                ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=reference_id, sender=request.user, title=title)
                entities_notified.save()
                
                # Create email
                send_email_notice_placed(project, community, researcher)
            
            return redirect('researcher-projects', researcher.id)

        context = {
            'researcher': researcher,
            'project': project,
            'communities': communities,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/notify.html', context)
        
@login_required(login_url='login')
def connections(request, pk):
    researcher = Researcher.objects.get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        connections = Connections.objects.get(researcher=researcher)
        context = {
            'researcher': researcher,
            'connections': connections,
            'user_can_view': user_can_view,
        }
        return render(request, 'researchers/connections.html', context)