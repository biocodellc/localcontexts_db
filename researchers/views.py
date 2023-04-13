from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from itertools import chain

from localcontexts.utils import dev_prod_or_local
from projects.utils import *
from helpers.utils import *
from accounts.utils import get_users_name
from notifications.utils import send_action_notification_to_project_contribs

from communities.models import Community
from notifications.models import ActionNotification
from helpers.models import *
from projects.models import *

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

                        send_contact_email(to_email, from_name, from_email, message, researcher)
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
    if not user_can_view:
        return redirect('restricted')
    else:
        bool_dict = {
            'has_labels': False,
            'has_notices': False,
            'created': False,
            'contributed': False,
            'is_archived': False,
            'title_az': False,
            'visibility_public': False,
            'visibility_contributor': False,
            'visibility_private': False,
            'date_modified': False
        }
    
        projects_list = list(chain(
            researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # researcher projects
            researcher.researchers_notified.all().values_list('project__unique_id', flat=True), # projects researcher has been notified of
            researcher.contributing_researchers.all().values_list('project__unique_id', flat=True), # projects where researcher is contributor
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_added')
        
        sort_by = request.GET.get('sort')

        if sort_by == 'all':
            return redirect('researcher-projects', researcher.id)
        
        elif sort_by == 'has_labels':
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
                ).exclude(unique_id__in=archived).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
                ).exclude(unique_id__in=archived).exclude(tk_labels=None).order_by('-date_added')
            bool_dict['has_labels'] = True
        
        elif sort_by == 'has_notices':
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, tk_labels=None, bc_labels=None).exclude(unique_id__in=archived).order_by('-date_added')
            bool_dict['has_notices'] = True

        elif sort_by == 'created':
            created_projects = researcher.researcher_created_project.all().values_list('project__unique_id', flat=True)
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=created_projects).exclude(unique_id__in=archived).order_by('-date_added')
            bool_dict['created'] = True

        elif sort_by == 'contributed':
            contrib = researcher.contributing_researchers.all().values_list('project__unique_id', flat=True)
            projects_list = list(chain(
                researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), # check researcher created projects
                ProjectArchived.objects.filter(project_uuid__in=contrib, researcher_id=researcher.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
            ))
            project_ids = list(set(projects_list)) # remove duplicate ids
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=contrib).exclude(unique_id__in=project_ids).order_by('-date_added')
            bool_dict['contributed'] = True

        elif sort_by == 'archived':
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=archived).order_by('-date_added')
            bool_dict['is_archived'] = True
        
        elif sort_by == 'title_az':
            projects = projects.order_by('title')
            bool_dict['title_az'] = True

        elif sort_by == 'visibility_public':
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Public').exclude(unique_id__in=archived).order_by('-date_added')
            bool_dict['visibility_public'] = True

        elif sort_by == 'visibility_contributor':
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Contributor').exclude(unique_id__in=archived).order_by('-date_added')
            bool_dict['visibility_contributor'] = True

        elif sort_by == 'visibility_private':
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, project_privacy='Private').exclude(unique_id__in=archived).order_by('-date_added')
            bool_dict['visibility_private'] = True

        elif sort_by == 'date_modified':
            projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_modified')
            bool_dict['date_modified'] = True
    
        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'researcher': researcher,
            'user_can_view': user_can_view,
            'items': page,
            'results': results,
            'bool_dict': bool_dict,
        }
        return render(request, 'researchers/projects.html', context)


# Create Project
@login_required(login_url='login')
def create_project(request, pk, source_proj_uuid=None, related=None):
    researcher = Researcher.objects.select_related('user').get(id=pk)
    name = get_users_name(request.user)

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

                if source_proj_uuid and not related:
                    data.source_project_uuid = source_proj_uuid
                    data.save()
                    ProjectActivity.objects.create(project=data, activity=f'Sub Project "{data.title}" was added to Project by {name} | Researcher')

                if source_proj_uuid and related:
                    source = Project.objects.get(unique_id=source_proj_uuid)
                    data.related_projects.add(source)
                    source.related_projects.add(data)
                    source.save()
                    data.save()

                    ProjectActivity.objects.create(project=data, activity=f'Project "{source.title}" was connected to Project by {name} | Researcher')
                    ProjectActivity.objects.create(project=source, activity=f'Project "{data.title}" was connected to Project by {name} | Researcher')

                # Create activity
                ProjectActivity.objects.create(project=data, activity=f'Project was created by {name} | Researcher')

                # Add project to researcher projects
                creator = ProjectCreator.objects.select_related('researcher').get(project=data)
                creator.researcher = researcher
                creator.save()

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                crud_notices(request, notices_selected, researcher, data, None)
            
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, researcher, data)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    if instance.name or instance.email:
                        instance.project = data
                        instance.save()
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id, researcher)
                
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
            notices = Notice.objects.filter(project=project, archived=False)

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
                crud_notices(request, notices_selected, researcher, data, notices)

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
            sub_projects = Project.objects.filter(source_project_uuid=project.unique_id).values_list('unique_id', 'title')
            name = get_users_name(request.user)

            # for related projects list
            projects_list = list(chain(
                researcher.researcher_created_project.all().values_list('project__unique_id', flat=True), 
                researcher.researchers_notified.all().values_list('project__unique_id', flat=True), 
                researcher.contributing_researchers.all().values_list('project__unique_id', flat=True),
            ))
            project_ids = list(set(projects_list)) # remove duplicate ids
            project_ids_to_exclude_list = list(project.related_projects.all().values_list('unique_id', flat=True)) #projects that are currently related

            # exclude projects that are already related
            for item in project_ids_to_exclude_list:
                if item in project_ids:
                    project_ids.remove(item)

            projects_to_link = Project.objects.filter(unique_id__in=project_ids).exclude(unique_id=project.unique_id).order_by('-date_added').values_list('unique_id', 'title')

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
                        send_action_notification_to_project_contribs(project)
                        return redirect('researcher-project-actions', researcher.id, project.unique_id)

                elif 'notify_btn' in request.POST: 
                    # Set private project to contributor view
                    if project.project_privacy == 'Private':
                        project.project_privacy = 'Contributor'
                        project.save()

                    communities_selected = request.POST.getlist('selected_communities')

                    researcher_name = get_users_name(researcher.user)
                    title =  f'{researcher_name} has notified you of a Project.'

                    for community_id in communities_selected:
                        # Add communities that were notified to entities_notified instance
                        community = Community.objects.get(id=community_id)
                        entities_notified.communities.add(community)
                        
                        # Add activity
                        ProjectActivity.objects.create(project=project, activity=f'{community.community_name} was notified by {name}')

                        # Create project status and  notification
                        ProjectStatus.objects.create(project=project, community=community, seen=False) # Creates a project status for each community
                        ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=str(project.unique_id), sender=request.user, title=title)
                        entities_notified.save()

                        # Create email 
                        send_email_notice_placed(request, project, community, researcher)
                        return redirect('researcher-project-actions', researcher.id, project.unique_id)
                elif 'link_projects_btn' in request.POST:
                    selected_projects = request.POST.getlist('projects_to_link')

                    for uuid in selected_projects:
                        project_to_add = Project.objects.get(unique_id=uuid)
                        project.related_projects.add(project_to_add)
                        project_to_add.related_projects.add(project)
                        project_to_add.save()

                        ProjectActivity.objects.create(project=project_to_add, activity=f'Project "{project_to_add}" was connected to Project "{project}" by {name}')
                        ProjectActivity.objects.create(project=project, activity=f'Project "{project}" was connected to Project "{project_to_add}" by {name}')
                    
                    project.save()
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
                'sub_projects': sub_projects,
                'projects_to_link': projects_to_link

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
def unlink_project(request, pk, target_proj_uuid, proj_to_remove_uuid):
    researcher = Researcher.objects.get(id=pk)
    target_project = Project.objects.get(unique_id=target_proj_uuid)
    project_to_remove = Project.objects.get(unique_id=proj_to_remove_uuid)
    target_project.related_projects.remove(project_to_remove)
    project_to_remove.related_projects.remove(target_project)
    target_project.save()
    project_to_remove.save()
    name = get_users_name(request.user)
    ProjectActivity.objects.create(project=project_to_remove, activity=f'Connection was removed between Project "{project_to_remove}" and Project "{target_project}" by {name}')
    ProjectActivity.objects.create(project=target_project, activity=f'Connection was removed between Project "{target_project}" and Project "{project_to_remove}" by {name}')
    return redirect('researcher-project-actions', researcher.id, target_project.unique_id)

        
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