from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
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
from helpers.models import OpenToCollaborateNoticeURL, ProjectStatus, ProjectComment, Notice, EntitiesNotified
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
        bcnotice = Notice.objects.filter(researcher=researcher, notice_type='biocultural').exists()
        tknotice = Notice.objects.filter(researcher=researcher, notice_type='traditional_knowledge').exists()
        attrnotice = Notice.objects.filter(researcher=researcher, notice_type='attribution_incomplete').exists()

        projects = []

        for p in created_projects:
            if p.project.project_privacy == 'Public':
                projects.append(p.project)
        
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(researcher=researcher)

        if request.user.is_authenticated:
            form = ContactOrganizationForm(request.POST or None)

            if request.method == 'POST':
                if 'contact_btn' in request.POST:
                    # contact researcher
                    if form.is_valid():
                        from_name = form.cleaned_data['name']
                        from_email = form.cleaned_data['email']
                        message = form.cleaned_data['message']
                        to_email = researcher.contact_email

                        send_contact_email(to_email, from_name, from_email, message)
                        messages.add_message(request, messages.SUCCESS, 'Message sent!')
                        return redirect('public-researcher', researcher.id)
                    else:
                        if not form.data['message']:
                            messages.add_message(request, messages.ERROR, 'Unable to send an empty message.')
                            return redirect('public-researcher', researcher.id)
                else:
                    messages.add_message(request, messages.ERROR, 'Something went wrong')
                    return redirect('public-researcher', researcher.id)
        else:
            context = { 
                'researcher': researcher,
                'projects' : projects,
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
            'form': form, 
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
        
        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'researcher': researcher,
            'user_can_view': user_can_view,
            'items': page,
            'results': results,
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
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__id', flat=True), 
            researcher.researchers_notified.all().values_list('project__id', flat=True), 
            researcher.contributing_researchers.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids

        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids
            ).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids
            ).exclude(tk_labels=None).order_by('-date_added')

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'researcher': researcher,
            'user_can_view': user_can_view,
            'items': page,
            'results': results,
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
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__id', flat=True), 
            researcher.researchers_notified.all().values_list('project__id', flat=True), 
            researcher.contributing_researchers.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids, tk_labels=None, bc_labels=None).order_by('-date_added')

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'researcher': researcher,
            'user_can_view': user_can_view,
            'items': page,
            'results': results,
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

        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)

        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'researcher': researcher,
            'user_can_view': user_can_view,
            'items': page,
            'results': results,
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


        p = Paginator(projects, 10)
        page_num = request.GET.get('page', 1)
        page = p.page(page_num)
        
        if request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'researcher': researcher,
            'user_can_view': user_can_view,
            'items': page,
            'results': results,
        }
        return render(request, 'researchers/projects.html', context)


# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    researcher = Researcher.objects.select_related('user').get(id=pk)
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
                
                # Handle multiple urls, save as array
                project_links = request.POST.getlist('project_urls')
                data.urls = project_links
                    
                data.save()

                # Add project to researcher projects
                creator = ProjectCreator.objects.select_related('researcher').get(project=data)
                creator.researcher = researcher
                creator.save()

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                create_notices(notices_selected, researcher, data, None)
            
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, researcher, data)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    if instance.name or instance.email:
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
        urls = project.urls

        # Check to see if notice exists for this project and pass to template
        if Notice.objects.filter(project=project).exists():
            notices = Notice.objects.filter(project=project)

        if request.method == 'POST':
            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                project_links = request.POST.getlist('project_urls')
                data.urls = project_links
                data.save()

                instances = formset.save(commit=False)
                for instance in instances:
                    if not instance.name or not instance.email:
                        instance.delete()
                    else:
                        instance.project = data
                        instance.save()

                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, researcher, data)
            
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
            'urls': urls,
        }
        return render(request, 'researchers/edit-project.html', context)

# @login_required(login_url='login')
def project_actions(request, pk, project_uuid):
    researcher = Researcher.objects.get(id=pk)
    project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('view-project', project.unique_id)
    else:
        project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
        notices = Notice.objects.filter(project=project, archived=False)
        creator = ProjectCreator.objects.get(project=project)
        
        form = ProjectCommentForm(request.POST or None)

        if request.method == 'POST':
            if request.POST.get('message'):
                if form.is_valid():
                    data = form.save(commit=False)
                    data.project = project
                    data.sender = request.user
                    data.sender_affiliation = 'Researcher'
                    data.save()
                    return redirect('researcher-project-actions', researcher.id, project.unique_id)

        context = {
            'user_can_view': user_can_view,
            'researcher': researcher,
            'project': project,
            'notices': notices,
            'creator': creator,
            'form': form,
        }
        return render(request, 'researchers/project-actions.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_others(request, pk, project_uuid):
    researcher = Researcher.objects.select_related('user').get(id=pk)

    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        project = Project.objects.prefetch_related('bc_labels', 'tk_labels', 'project_status').get(unique_id=project_uuid)
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

        researchers = Researcher.objects.none()

        institution_ids = researcher.contributing_researchers.exclude(institutions__id=None).values_list('institutions__id', flat=True)
        institutions = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').filter(id__in=institution_ids)
    
        community_ids = researcher.contributing_researchers.exclude(communities__id=None).values_list('communities__id', flat=True)
        communities = Community.objects.select_related('community_creator').filter(id__in=community_ids)
        
        project_ids = researcher.contributing_researchers.values_list('project__unique_id', flat=True)
        contributors = ProjectContributors.objects.filter(project__unique_id__in=project_ids)
        for c in contributors:
            researchers = c.researchers.select_related('user').exclude(id=researcher.id)

        context = {
            'researcher': researcher,
            'user_can_view': user_can_view,
            'communities': communities,
            'researchers': researchers,
            'institutions': institutions,
        }
        return render(request, 'researchers/connections.html', context)