from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator
from itertools import chain

from localcontexts.utils import dev_prod_or_local
from projects.utils import *
from helpers.utils import *
from accounts.utils import get_users_name

from communities.models import Community
from notifications.models import ActionNotification
from helpers.models import *
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
        urls = OpenToCollaborateNoticeURL.objects.filter(researcher=researcher).values_list('url', 'name', 'id')
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
def delete_otc_notice(request, researcher_id, notice_id):
    if OpenToCollaborateNoticeURL.objects.filter(id=notice_id).exists():
        otc = OpenToCollaborateNoticeURL.objects.get(id=notice_id)
        otc.delete()
    return redirect('researcher-notices', researcher_id)


@login_required(login_url='login')
def researcher_projects(request, pk):
    researcher = Researcher.objects.prefetch_related('user').get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # researcher projects
            researcher.researchers_notified.all().values_list('project__unique_id', flat=True), # projects researcher has been notified of
            researcher.contributing_researchers.all().values_list('project__unique_id', flat=True), # projects where researcher is contributor
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_added')
        
        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

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
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # researcher projects
            researcher.researchers_notified.all().values_list('project__unique_id', flat=True), # projects researcher has been notified of 
            researcher.contributing_researchers.all().values_list('project__unique_id', flat=True), # projects where researcher is contributor
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(tk_labels=None).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

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
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # researcher projects
            researcher.researchers_notified.all().values_list('project__unique_id', flat=True), # projects researcher has been notified of 
            researcher.contributing_researchers.all().values_list('project__unique_id', flat=True), # projects where researcher is contributor
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, tk_labels=None, bc_labels=None).exclude(unique_id__in=archived).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

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
        created_projects = researcher.researcher_created_project.all().values_list('project__unique_id', flat=True)
        archived = ProjectArchived.objects.filter(project_uuid__in=created_projects, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=created_projects).exclude(unique_id__in=archived).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

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
        contrib = researcher.contributing_researchers.all().values_list('project__unique_id', flat=True)
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # check researcher created projects
            ProjectArchived.objects.filter(project_uuid__in=contrib, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=contrib).exclude(unique_id__in=project_ids).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'researcher': researcher,
            'user_can_view': user_can_view,
            'items': page,
            'results': results,
        }
        return render(request, 'researchers/projects.html', context)

@login_required(login_url='login')
def projects_archived(request, pk):
    researcher = Researcher.objects.select_related('user').get(id=pk)
    user_can_view = checkif_user_researcher(researcher, request.user)
    if user_can_view == False:
        return redirect('restricted')
    else:
        archived_projects = ProjectArchived.objects.filter(researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=archived_projects).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'researcher': researcher,
            'items': page,
            'results': results,
            'user_can_view': user_can_view,
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

                # Create activity
                name = get_users_name(request.user)
                ProjectActivity.objects.create(project=data, activity=f'Project was created by {name} | Researcher')


                # Add project to researcher projects
                creator = ProjectCreator.objects.select_related('researcher').get(project=data)
                creator.researcher = researcher
                creator.save()

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                crud_notices(notices_selected, researcher, data, None)
            
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

                editor_name = get_users_name(request.user)
                ProjectActivity.objects.create(project=data, activity=f'Edits to Project were made by {editor_name}')

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
                crud_notices(notices_selected, researcher, data, notices)

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
    project = Project.objects.prefetch_related(
                'bc_labels', 
                'tk_labels', 
                'bc_labels__community', 
                'tk_labels__community',
                'bc_labels__bclabel_translation', 
                'tk_labels__tklabel_translation',
                ).get(unique_id=project_uuid)

    if request.user.is_authenticated:
        researcher = Researcher.objects.get(id=pk)

        user_can_view = checkif_user_researcher(researcher, request.user)
        if user_can_view == False:
            return redirect('view-project', project.unique_id)
        else:
            notices = Notice.objects.filter(project=project, archived=False)
            creator = ProjectCreator.objects.get(project=project)
            statuses = ProjectStatus.objects.select_related('community').filter(project=project)
            comments = ProjectComment.objects.select_related('sender').filter(project=project)
            entities_notified = EntitiesNotified.objects.get(project=project)
            activities = ProjectActivity.objects.filter(project=project).order_by('-date')

            project_archived = False
            if ProjectArchived.objects.filter(project_uuid=project.unique_id, researcher_id=researcher.id).exists():
                x = ProjectArchived.objects.get(project_uuid=project.unique_id, researcher_id=researcher.id)
                project_archived = x.archived
            form = ProjectCommentForm(request.POST or None)

            communities_list = list(chain(
                project.project_status.all().values_list('community__id', flat=True),
            ))

            if creator.community:
                communities_list.append(creator.community.id)

            communities_ids = list(set(communities_list)) # remove duplicate ids
            communities = Community.approved.exclude(id__in=communities_ids).order_by('community_name')

            if request.method == 'POST':
                if request.POST.get('message'):
                    if form.is_valid():
                        data = form.save(commit=False)
                        data.project = project
                        data.sender = request.user
                        data.sender_affiliation = 'Researcher'
                        data.save()
                        return redirect('researcher-project-actions', researcher.id, project.unique_id)

                elif 'notify_btn' in request.POST: 
                    # Set private project to discoverable
                    if project.project_privacy == 'Private':
                        project.project_privacy = 'Discoverable'
                        project.save()

                    communities_selected = request.POST.getlist('selected_communities')
                    message = request.POST.get('notice_message')

                    name = get_users_name(researcher.user)
                    title =  f'{name} has notified you of a Project.'

                    for community_id in communities_selected:
                        # Add communities that were notified to entities_notified instance
                        community = Community.objects.get(id=community_id)
                        entities_notified.communities.add(community)

                        # Add activity
                        ProjectActivity.objects.create(project=project, activity=f'{community.community_name} was notified')

                        # Create project status, first comment and  notification
                        ProjectStatus.objects.create(project=project, community=community, seen=False) # Creates a project status for each community
                        if message:
                            ProjectComment.objects.create(project=project, community=community, sender=request.user, sender_affiliation='Researcher', message=message)
                        ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=str(project.unique_id), sender=request.user, title=title)
                        entities_notified.save()

                        # Create email 
                        send_email_notice_placed(project, community, researcher)
                        return redirect('researcher-project-actions', researcher.id, project.unique_id)

                elif 'delete_project' in request.POST:
                    return redirect('researcher-delete-project', researcher.id, project.unique_id)

            context = {
                'user_can_view': user_can_view,
                'researcher': researcher,
                'project': project,
                'notices': notices,
                'creator': creator,
                'form': form,
                'communities': communities,
                'statuses': statuses,
                'comments': comments,
                'activities': activities,
                'project_archived': project_archived,
            }
            return render(request, 'researchers/project-actions.html', context)
    else:
        return redirect('view-project', project.unique_id)

@login_required(login_url='login')
def archive_project(request, researcher_id, project_uuid):
    if not ProjectArchived.objects.filter(researcher_id=researcher_id, project_uuid=project_uuid).exists():
        ProjectArchived.objects.create(researcher_id=researcher_id, project_uuid=project_uuid, archived=True)
    else:
        archived_project = ProjectArchived.objects.get(researcher_id=researcher_id, project_uuid=project_uuid)
        if archived_project.archived:
            archived_project.archived = False
        else:
            archived_project.archived = True
        archived_project.save()
    return redirect('researcher-project-actions', researcher_id, project_uuid)


@login_required(login_url='login')
def delete_project(request, researcher_id, project_uuid):
    researcher = Researcher.objects.get(id=researcher_id)
    project = Project.objects.get(unique_id=project_uuid)

    if ActionNotification.objects.filter(reference_id=project.unique_id).exists():
        for notification in ActionNotification.objects.filter(reference_id=project.unique_id):
            notification.delete()
    
    project.delete()
    return redirect('researcher-projects', researcher.id)

        
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