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

from .models import *
from projects.models import Project, ProjectContributors, ProjectPerson, ProjectCreator
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from helpers.models import *

from django.contrib.auth.models import User
from accounts.models import UserAffiliation

from projects.forms import *
from helpers.forms import ProjectCommentForm, OpenToCollaborateNoticeURLForm
from communities.forms import InviteMemberForm, JoinRequestForm
from accounts.forms import ContactOrganizationForm
from .forms import *

from helpers.emails import *

@login_required(login_url='login')
def connect_institution(request):
    institution = True
    institutions = Institution.approved.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        institution_name = request.POST.get('organization_name')
        if Institution.objects.filter(institution_name=institution_name).exists():
            institution = Institution.objects.get(institution_name=institution_name)

            # If join request exists or user is already a member, display Error message
            request_exists = JoinRequest.objects.filter(user_from=request.user, institution=institution).exists()
            user_is_member = institution.is_user_in_institution(request.user)

            if request_exists or user_is_member:
                messages.add_message(request, messages.ERROR, "Either you have already sent this request or are currently a member of this institution.")
                return redirect('connect-institution')
            else:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.user_from = request.user
                    data.institution = institution
                    data.user_to = institution.institution_creator
                    data.save()

                    # Send institution creator email
                    send_join_request_email_admin(request, data, institution)
                    messages.add_message(request, messages.SUCCESS, "Request to join institution sent!")
                    return redirect('connect-institution')
        else:
            messages.add_message(request, messages.ERROR, 'Institution not in registry')
            return redirect('connect-institution')

    context = { 'institution': institution, 'institutions': institutions, 'form': form,}
    return render(request, 'institutions/connect-institution.html', context)

@login_required(login_url='login')
def preparation_step(request):
    institution = True
    return render(request, 'accounts/preparation.html', { 'institution': institution })

@login_required(login_url='login')
def create_institution(request):
    form = CreateInstitutionForm(request.POST or None)
    noror_form = CreateInstitutionNoRorForm(request.POST or None)

    if request.method == 'POST':
        affiliation = UserAffiliation.objects.prefetch_related('institutions').get(user=request.user)

        if 'create-institution-btn' in request.POST:
            if form.is_valid():
                name = request.POST.get('institution_name')
                data = form.save(commit=False)

                if Institution.objects.filter(institution_name=name).exists():
                    messages.add_message(request, messages.ERROR, 'An institution by this name already exists.')
                    return redirect('create-institution')
                else:
                    data.institution_name = name
                    data.institution_creator = request.user

                    # If in test site, approve immediately, skip confirmation step
                    if dev_prod_or_local(request.get_host()) == 'DEV':
                        data.is_approved = True
                        data.save()
                        
                        # Add to user affiliations
                        affiliation.institutions.add(data)
                        affiliation.save()
                        return redirect('dashboard')
                    else:
                        data.save()

                        # Add to user affiliations
                        affiliation.institutions.add(data)
                        affiliation.save()
                        return redirect('confirm-institution', data.id)
        elif 'create-institution-noror-btn' in request.POST:
            if noror_form.is_valid():
                data = noror_form.save(commit=False)
                data.institution_creator = request.user
                data.is_ror = False
                data.save()

                # Add to user affiliations
                affiliation.institutions.add(data)
                affiliation.save()
                return redirect('confirm-institution', data.id)
    return render(request, 'institutions/create-institution.html', {'form': form, 'noror_form': noror_form,})

@login_required(login_url='login')
def confirm_institution(request, institution_id):
    institution = Institution.objects.get(id=institution_id)

    form = ConfirmInstitutionForm(request.POST or None, request.FILES, instance=institution)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            # If in test site, approve immediately, skip confirmation step
            if dev_prod_or_local(request.get_host()) == 'DEV':
                data.is_approved = True
                data.save()
                return redirect('dashboard')
            else:
                data.save()
                send_hub_admins_application_email(request, institution, data)
                return redirect('dashboard')
    return render(request, 'accounts/confirm-account.html', {'form': form, 'institution': institution,})

def public_institution_view(request, pk):
    try:
        institution = Institution.objects.get(id=pk)
        created_projects = ProjectCreator.objects.filter(institution=institution)

        # Do notices exist
        bcnotice = Notice.objects.filter(institution=institution, notice_type='biocultural').exists()
        tknotice = Notice.objects.filter(institution=institution, notice_type='traditional_knowledge').exists()
        attrnotice = Notice.objects.filter(institution=institution, notice_type='attribution_incomplete').exists()

        projects = []

        for p in created_projects:
            if p.project.project_privacy == 'Public':
                projects.append(p.project)
        
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(institution=institution)
        
        if request.user.is_authenticated:
            user_institutions = UserAffiliation.objects.prefetch_related('institutions').get(user=request.user).institutions.all()
            form = ContactOrganizationForm(request.POST or None)
            join_form = JoinRequestForm(request.POST or None)

            if request.method == 'POST':
                if 'contact_btn' in request.POST:
                    # contact institution
                    if form.is_valid():
                        from_name = form.cleaned_data['name']
                        from_email = form.cleaned_data['email']
                        message = form.cleaned_data['message']
                        to_email = institution.institution_creator.email
                        
                        send_contact_email(to_email, from_name, from_email, message)
                        messages.add_message(request, messages.SUCCESS, 'Message sent!')
                        return redirect('public-institution', institution.id)
                    else:
                        if not form.data['message']:
                            messages.add_message(request, messages.ERROR, 'Unable to send an empty message.')
                            return redirect('public-institution', institution.id)

                elif 'join_request' in request.POST:
                    if join_form.is_valid():
                        data = join_form.save(commit=False)
                        if JoinRequest.objects.filter(user_from=request.user, institution=institution).exists():
                            messages.add_message(request, messages.ERROR, "You have already sent a request to this institution")
                            return redirect('public-institution', institution.id)
                        else:
                            data.user_from = request.user
                            data.institution = institution
                            data.user_to = institution.institution_creator
                            data.save()

                            # Send email to institution creator
                            send_join_request_email_admin(request, data, institution)
                            messages.add_message(request, messages.SUCCESS, 'Request sent!')
                            return redirect('public-institution', institution.id)
                else:
                    messages.add_message(request, messages.ERROR, 'Something went wrong')
                    return redirect('public-institution', institution.id)

        else:
            context = { 
                'institution': institution,
                'projects' : projects,
                'bcnotice': bcnotice,
                'tknotice': tknotice,
                'attrnotice': attrnotice,
                'otc_notices': otc_notices,
            }
            return render(request, 'public.html', context)

        context = { 
            'institution': institution,
            'projects' : projects,
            'form': form, 
            'join_form': join_form,
            'user_institutions': user_institutions,
            'bcnotice': bcnotice,
            'tknotice': tknotice,
            'attrnotice': attrnotice,
            'otc_notices': otc_notices,
        }
        return render(request, 'public.html', context)
    except:
        raise Http404()

# Update institution
@login_required(login_url='login')
def update_institution(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')

    else:
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
            'member_role': member_role,
        }

        return render(request, 'institutions/update-institution.html', context)

# Notices
@login_required(login_url='login')
def institution_notices(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('public-institution', institution.id)
    else:
        urls = OpenToCollaborateNoticeURL.objects.filter(institution=institution).values_list('url', 'name', 'id')
        form = OpenToCollaborateNoticeURLForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                data = form.save(commit=False)
                data.institution = institution
                data.save()
            return redirect('institution-notices', institution.id)

        context = {
            'institution': institution,
            'member_role': member_role,
            'form': form,
            'urls': urls,
        }
        return render(request, 'institutions/notices.html', context)

@login_required(login_url='login')
def delete_otc_notice(request, institution_id, notice_id):
    if OpenToCollaborateNoticeURL.objects.filter(id=notice_id).exists():
        otc = OpenToCollaborateNoticeURL.objects.get(id=notice_id)
        otc.delete()
    return redirect('institution-notices', institution_id)

# Members
@login_required(login_url='login')
def institution_members(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # Get list of users, NOT in this institution, alphabetized by name
        members = list(chain(
            institution.admins.all().values_list('id', flat=True), 
            institution.editors.all().values_list('id', flat=True), 
            institution.viewers.all().values_list('id', flat=True),
        ))
        members.append(institution.institution_creator.id) # include institution creator
        users = User.objects.exclude(id__in=members).order_by('username')

        join_requests_count = JoinRequest.objects.filter(institution=institution).count()
        form = InviteMemberForm(request.POST or None)

        if request.method == 'POST':
            if 'change_member_role_btn' in request.POST:
                current_role = request.POST.get('current_role')
                new_role = request.POST.get('new_role')
                user_id = request.POST.get('user_id')
                member = User.objects.get(id=user_id)
                change_member_role(institution, member, current_role, new_role)
                return redirect('institution-members', institution.id)

            elif 'send_invite_btn' in request.POST:
                selected_user = User.objects.none()
                if form.is_valid():
                    data = form.save(commit=False)

                    # Get target User
                    selected_username = request.POST.get('userList')
                    username_to_check = ''

                    if ' ' in selected_username: #if username includes spaces means it has a first and last name (last name,first name)
                        x = selected_username.split(' ')
                        username_to_check = x[0]
                    else:
                        username_to_check = selected_username

                    if not username_to_check in users.values_list('username', flat=True):
                        messages.add_message(request, messages.INFO, 'Invalid user selection. Please select user from the list.')
                    else:
                        selected_user = User.objects.get(username=username_to_check)
    
                        # Check to see if an invite or join request aleady exists
                        invitation_exists = InviteMember.objects.filter(receiver=selected_user, institution=institution).exists() # Check to see if invitation already exists
                        join_request_exists = JoinRequest.objects.filter(user_from=selected_user, institution=institution).exists() # Check to see if join request already exists

                        if not invitation_exists and not join_request_exists: # If invitation and join request does not exist, save form
                            data.receiver = selected_user
                            data.sender = request.user
                            data.status = 'sent'
                            data.institution = institution
                            data.save()
                            
                            send_institution_invite_email(request, data, institution) # Send email to target user
                            messages.add_message(request, messages.INFO, f'Invitation sent to {selected_user}')
                            return redirect('institution-members', institution.id)
                        else: 
                            messages.add_message(request, messages.INFO, f'The user you are trying to add already has an invitation pending to join {institution.institution_name}.')
                else:
                    messages.add_message(request, messages.INFO, 'Something went wrong')

        context = { 
            'institution': institution,
            'form': form,
            'member_role': member_role,
            'join_requests_count': join_requests_count,
            'users': users,
        }    
        return render(request, 'institutions/members.html', context)

@login_required(login_url='login')
def member_requests(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        join_requests = JoinRequest.objects.filter(institution=institution)
        member_invites = InviteMember.objects.filter(institution=institution)
        
        if request.method == 'POST':
            selected_role = request.POST.get('selected_role')
            join_request_id = request.POST.get('join_request_id')

            accepted_join_request(institution, join_request_id, selected_role)
            messages.add_message(request, messages.SUCCESS, 'You have successfully added a new member!')
            return redirect('institution-member-requests', institution.id)

        context = {
            'member_role': member_role,
            'institution': institution,
            'join_requests': join_requests,
            'member_invites': member_invites,
        }
        return render(request, 'institutions/member-requests.html', context)

@login_required(login_url='login')
def delete_join_request(request, pk, join_id):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    join_request = JoinRequest.objects.get(id=join_id)
    join_request.delete()
    return redirect('institution-member-requests', institution.id)
    
@login_required(login_url='login')
def remove_member(request, pk, member_id):
    institution = Institution.objects.prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    member = User.objects.get(id=member_id)
    # what role does member have
    # remove from role
    if member in institution.admins.all():
        institution.admins.remove(member)
    if member in institution.editors.all():
        institution.editors.remove(member)
    if member in institution.viewers.all():
        institution.viewers.remove(member)

    # remove institution from userAffiliation instance
    affiliation = UserAffiliation.objects.prefetch_related('institutions').get(user=member)
    affiliation.institutions.remove(institution)

    # Delete join request for this institution if exists
    if JoinRequest.objects.filter(user_from=member, institution=institution).exists():
        join_request = JoinRequest.objects.get(user_from=member, institution=institution)
        join_request.delete()

    if '/manage/' in request.META.get('HTTP_REFERER'):
        return redirect('manage-orgs')
    else:
        return redirect('institution-members', institution.id)

# Projects: all 
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # 1. institution projects + 
        # 2. projects institution has been notified of 
        # 3. projects where institution is contributor

        projects_list = list(chain(
            institution.institution_created_project.all().values_list('project__unique_id', flat=True), 
            institution.institutions_notified.all().values_list('project__unique_id', flat=True), 
            institution.contributing_institutions.all().values_list('project__unique_id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, institution_id=institution.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids).exclude(unique_id__in=archived).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'institution': institution,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_with_labels(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # init list for:
        # 1. institution projects + 
        # 2. projects institution has been notified of 
        # 3. projects where institution is contributor
        projects_list = list(chain(
            institution.institution_created_project.all().values_list('project__unique_id', flat=True), 
            institution.institutions_notified.all().values_list('project__unique_id', flat=True), 
            institution.contributing_institutions.all().values_list('project__unique_id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, institution_id=institution.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids
            ).exclude(unique_id__in=archived).exclude(tk_labels=None).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'institution': institution,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'institutions/projects.html', context)


@login_required(login_url='login')
def projects_with_notices(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # init list for:
        # 1. institution projects + 
        # 2. projects institution has been notified of 
        # 3. projects where institution is contributor
        projects_list = list(chain(
            institution.institution_created_project.all().values_list('project__unique_id', flat=True), 
            institution.institutions_notified.all().values_list('project__unique_id', flat=True), 
            institution.contributing_institutions.all().values_list('project__unique_id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        archived = ProjectArchived.objects.filter(project_uuid__in=project_ids, institution_id=institution.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=project_ids, tk_labels=None, bc_labels=None).exclude(unique_id__in=archived).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'institution': institution,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_creator(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        created_projects = institution.institution_created_project.all().values_list('project__unique_id', flat=True)
        archived = ProjectArchived.objects.filter(project_uuid__in=created_projects, institution_id=institution.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=created_projects).exclude(unique_id__in=archived).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'institution': institution,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'institutions/projects.html', context)


@login_required(login_url='login')
def projects_contributor(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        contrib = institution.contributing_institutions.all().values_list('project__unique_id', flat=True)
        projects_list = list(chain(
            institution.institution_created_project.all().values_list('project__unique_id', flat=True), # check institution created projects
            ProjectArchived.objects.filter(project_uuid__in=contrib, institution_id=institution.id, archived=True).values_list('project_uuid', flat=True) # check ids to see if they are archived
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=contrib).exclude(unique_id__in=project_ids).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'institution': institution,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_archived(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')    
    else:
        archived_projects = ProjectArchived.objects.filter(institution_id=institution.id, archived=True).values_list('project_uuid', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(unique_id__in=archived_projects).order_by('-date_added')

        page = paginate(request, projects, 10)
        
        if request.method == 'GET':
            results = return_project_search_results(request, projects)

        context = {
            'projects': projects,
            'institution': institution,
            'member_role': member_role,
            'items': page,
            'results': results,
        }
        return render(request, 'institutions/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    institution = Institution.objects.select_related('institution_creator').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / is a viewer.
        return redirect('restricted')
    else:
        if request.method == 'GET':
            form = CreateProjectForm(request.GET or None)
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
                name = get_users_name(data.project_creator)
                ProjectActivity.objects.create(project=data, activity=f'Project was created by {name} | {institution.institution_name}')

                # Add project to institution projects
                creator = ProjectCreator.objects.select_related('institution').get(project=data)
                creator.institution = institution
                creator.save()

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                crud_notices(notices_selected, institution, data, None)
                
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, institution, data)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    if instance.name or instance.email:
                        instance.project = data
                        instance.save()
                    
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id)

                # Format and send notification about the created project
                truncated_project_title = str(data.title)[0:30]
                title = f'A new project was created by {name}: {truncated_project_title} ...'
                ActionNotification.objects.create(title=title, notification_type='Projects', sender=data.project_creator, reference_id=data.unique_id, institution=institution)
                return redirect('institution-projects', institution.id)

        context = {
            'institution': institution,
            'form': form,
            'formset': formset,
            'member_role': member_role,
        }
        return render(request, 'institutions/create-project.html', context)

@login_required(login_url='login')
def edit_project(request, institution_id, project_uuid):
    institution = Institution.objects.get(id=institution_id)
    project = Project.objects.get(unique_id=project_uuid)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / is a viewer.
        return redirect('restricted')
    else:
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
                add_to_contributors(request, institution, data)

                # Which notices were selected to change
                notices_selected = request.POST.getlist('checkbox-notice')
                # Pass any existing notices as well as newly selected ones
                crud_notices(notices_selected, institution, data, notices)

            return redirect('institution-projects', institution.id)

        context = {
            'member_role': member_role,
            'institution': institution, 
            'project': project, 
            'notices': notices, 
            'form': form,
            'formset': formset,
            'contributors': contributors,
            'urls': urls,
        }
        return render(request, 'institutions/edit-project.html', context)

# @login_required(login_url='login')
def project_actions(request, pk, project_uuid):
    institution = Institution.objects.get(id=pk)
    project = Project.objects.prefetch_related(
            'bc_labels', 
            'tk_labels', 
            'bc_labels__community', 
            'tk_labels__community',
            'bc_labels__bclabel_translation', 
            'tk_labels__tklabel_translation',
            ).get(unique_id=project_uuid)

    member_role = check_member_role(request.user, institution)
    if member_role == False or not request.user.is_authenticated:
        return redirect('view-project', project_uuid)    
    else:
        notices = Notice.objects.filter(project=project, archived=False)
        creator = ProjectCreator.objects.get(project=project)
        statuses = ProjectStatus.objects.select_related('community').filter(project=project)
        comments = ProjectComment.objects.select_related('sender').filter(project=project)
        entities_notified = EntitiesNotified.objects.get(project=project)
        communities = Community.approved.all()
        activities = ProjectActivity.objects.filter(project=project).order_by('-date')

        project_archived = False
        if ProjectArchived.objects.filter(project_uuid=project.unique_id, institution_id=institution.id).exists():
            x = ProjectArchived.objects.get(project_uuid=project.unique_id, institution_id=institution.id)
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
                    data.sender_affiliation = institution.institution_name
                    data.save()
                    return redirect('institution-project-actions', institution.id, project.unique_id)
            
            elif 'notify_btn' in request.POST: 
                # Set private project to discoverable
                if project.project_privacy == 'Private':
                    project.project_privacy = 'Discoverable'
                    project.save()

                communities_selected = request.POST.getlist('selected_communities')
                message = request.POST.get('notice_message')

                # Reference ID and title for notification
                title =  str(institution.institution_name) + ' has notified you of a Project.'

                for community_id in communities_selected:
                    # Add communities that were notified to entities_notified instance
                    community = Community.objects.get(id=community_id)
                    entities_notified.communities.add(community)

                    # Add activity
                    ProjectActivity.objects.create(project=project, activity=f'{community.community_name} was notified')

                    # Create project status, first comment and  notification
                    ProjectStatus.objects.create(project=project, community=community, seen=False) # Creates a project status for each community
                    if message:
                        ProjectComment.objects.create(project=project, community=community, sender=request.user, sender_affiliation=institution.institution_name, message=message)
                    ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=str(project.unique_id), sender=request.user, title=title)
                    entities_notified.save()

                    # Create email 
                    send_email_notice_placed(project, community, institution)
                    return redirect('institution-project-actions', institution.id, project.unique_id)

            elif 'delete_project' in request.POST:
                return redirect('inst-delete-project', institution.id, project.unique_id)

        context = {
            'member_role': member_role,
            'institution': institution,
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
        return render(request, 'institutions/project-actions.html', context)

@login_required(login_url='login')
def archive_project(request, institution_id, project_uuid):
    if not ProjectArchived.objects.filter(institution_id=institution_id, project_uuid=project_uuid).exists():
        ProjectArchived.objects.create(institution_id=institution_id, project_uuid=project_uuid, archived=True)
    else:
        archived_project = ProjectArchived.objects.get(institution_id=institution_id, project_uuid=project_uuid)
        if archived_project.archived:
            archived_project.archived = False
        else:
            archived_project.archived = True
        archived_project.save()
    return redirect('institution-project-actions', institution_id, project_uuid)

@login_required(login_url='login')
def delete_project(request, institution_id, project_uuid):
    institution = Institution.objects.get(id=institution_id)
    project = Project.objects.get(unique_id=project_uuid)

    if ActionNotification.objects.filter(reference_id=project.unique_id).exists():
        for notification in ActionNotification.objects.filter(reference_id=project.unique_id):
            notification.delete()
    
    project.delete()
    return redirect('institution-projects', institution.id)

@login_required(login_url='login')
def connections(request, pk):
    institution = Institution.objects.select_related('institution_creator').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        institutions = Institution.objects.none()

        researcher_ids = institution.contributing_institutions.exclude(researchers__id=None).values_list('researchers__id', flat=True)
        community_ids = institution.contributing_institutions.exclude(communities__id=None).values_list('communities__id', flat=True)

        communities = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').filter(id__in=community_ids)
        researchers = Researcher.objects.select_related('user').filter(id__in=researcher_ids)
        
        project_ids = institution.contributing_institutions.values_list('project__unique_id', flat=True)
        contributors = ProjectContributors.objects.filter(project__unique_id__in=project_ids)
        for c in contributors:
            institutions = c.institutions.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').exclude(id=institution.id)

        context = {
            'member_role': member_role,
            'institution': institution,
            'communities': communities,
            'researchers': researchers,
            'institutions': institutions,
        }
        return render(request, 'institutions/connections.html', context)
