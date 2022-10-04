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

from .models import *
from projects.models import Project, ProjectContributors, ProjectPerson, ProjectCreator
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from helpers.models import ProjectComment, ProjectStatus, Notice, EntitiesNotified, OpenToCollaborateNoticeURL

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
        bcnotice = False
        tknotice = False
        attrnotice = False
        if Notice.objects.filter(institution=institution, notice_type='biocultural').exists():
            bcnotice = True
        if Notice.objects.filter(institution=institution, notice_type='traditional_knowledge').exists():
            tknotice = True
        if Notice.objects.filter(institution=institution, notice_type='attribution_incomplete').exists():
            attrnotice = True

        projects = []

        for p in created_projects:
            if p.project.project_privacy == 'Public':
                projects.append(p.project)
        
        otc_notices = OpenToCollaborateNoticeURL.objects.filter(institution=institution)
        
        if request.user.is_authenticated:
            user_institutions = UserAffiliation.objects.prefetch_related('institutions').get(user=request.user).institutions.all()
            form = ContactOrganizationForm(request.POST or None)

            if request.method == 'POST':
                if 'contact_btn' in request.POST:
                    # contact institution
                    if form.is_valid():
                        to_email = ''
                        from_name = form.cleaned_data['name']
                        from_email = form.cleaned_data['email']
                        message = form.cleaned_data['message']
                        to_email = institution.institution_creator.email
                        
                        send_contact_email(to_email, from_name, from_email, message)
                        messages.add_message(request, messages.SUCCESS, 'Sent!')
                        return redirect('public-institution', institution.id)
                else:
                    if JoinRequest.objects.filter(user_from=request.user, institution=institution).exists():
                        messages.add_message(request, messages.ERROR, "You have already sent a request to this institution")
                        return redirect('public-institution', institution.id)
                    else:
                        # Request To Join institution
                        join_request = JoinRequest.objects.create(user_from=request.user, institution=institution, user_to=institution.institution_creator)
                        join_request.save()

                        # Send email to institution creator
                        send_join_request_email_admin(request, join_request, institution)

                        messages.add_message(request, messages.SUCCESS, 'Sent!')
                return redirect('public-institution', institution.id)

            else:
                context = { 
                    'institution': institution,
                    'projects' : projects,
                    'form': form, 
                    'user_institutions': user_institutions,
                    'bcnotice': bcnotice,
                    'tknotice': tknotice,
                    'attrnotice': attrnotice,
                    'otc_notices': otc_notices,
                }
                return render(request, 'public.html', context)

        context = { 
            'institution': institution,
            'projects' : projects,
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
        urls = OpenToCollaborateNoticeURL.objects.filter(institution=institution).values_list('url', 'name')
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
            institution.institution_created_project.all().values_list('project__id', flat=True), 
            institution.institutions_notified.all().values_list('project__id', flat=True), 
            institution.contributing_institutions.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids).order_by('-date_added')

        p = Paginator(projects, 10)
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
                    return redirect('institution-projects', institution.id)
            else:
                return redirect('institution-projects', institution.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
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
            institution.institution_created_project.all().values_list('project__id', flat=True), 
            institution.institutions_notified.all().values_list('project__id', flat=True), 
            institution.contributing_institutions.all().values_list('project__id', flat=True),
        ))
        project_ids = list(set(projects_list)) # remove duplicate ids

        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids
            ).exclude(bc_labels=None).order_by('-date_added') | Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=project_ids
            ).exclude(tk_labels=None).order_by('-date_added')

        p = Paginator(projects, 10)
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
                    return redirect('institution-projects-labels', institution.id)
            else:
                return redirect('institution-projects-labels', institution.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
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
        projects_list = []

        for p in institution.institution_created_project.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if p.project.has_notice():
                projects_list.append(p.project)

        for n in institution.institutions_notified.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if n.project.has_notice():
                projects_list.append(n.project)
        
        for c in institution.contributing_institutions.select_related('project', 'project__project_creator').prefetch_related('project__bc_labels', 'project__tk_labels').all():
            if c.project.has_notice():
                projects_list.append(c.project)

        projects = list(set(projects_list))

        p = Paginator(projects, 10)
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
                    return redirect('institution-projects-notices', institution.id)
            else:
                return redirect('institution-projects-notices', institution.id)

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
            'member_role': member_role,
            'items': page,
        }
        return render(request, 'institutions/projects.html', context)

@login_required(login_url='login')
def projects_creator(request, pk):
    institution = Institution.objects.select_related('institution_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        created_projects = institution.institution_created_project.all().values_list('project__id', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=created_projects).order_by('-date_added')
        
        p = Paginator(projects, 10)
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
                    return redirect('institution-projects-creator', institution.id)
            else:
                return redirect('institution-projects-creator', institution.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
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
        # Get IDs of projects created by institution and IDs of projects contributed, then exclude the created ones in the project call
        created_projects = institution.institution_created_project.all().values_list('project__id', flat=True)
        contrib = institution.contributing_institutions.all().values_list('project__id', flat=True)
        projects = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').filter(id__in=contrib).exclude(id__in=created_projects).order_by('-date_added')

        p = Paginator(projects, 10)
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
                    return redirect('institution-projects-contributor', institution.id)
            else:
                return redirect('institution-projects-contributor', institution.id)
        elif request.method == 'GET':
            q = request.GET.get('q')
            if q:
                vector = SearchVector('title', 'description', 'unique_id', 'providers_id')
                query = SearchQuery(q)
                results = projects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.001).order_by('-rank') # project.rank returns a num
            else:
                results = None

        context = {
            'projects': projects,
            'institution': institution,
            'form': form,
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
                data.save()
                
                # Add project to institution projects
                creator = ProjectCreator.objects.select_related('institution').get(project=data)
                creator.institution = institution
                creator.save()

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                create_notices(notices_selected, institution, data, None)

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                 # Get a project contributor object and add institution to it.
                contributors = ProjectContributors.objects.prefetch_related('institutions').get(project=data)
                contributors.institutions.add(institution)
                
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()
                    
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id)

                # Format and send notification about the created project
                truncated_project_title = str(data.title)[0:30]
                name = get_users_name(data.project_creator)
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
                # Pass any existing notices as well as newly selected ones
                create_notices(notices_selected, institution, data, notices)

            return redirect('institution-projects', institution.id)

        context = {
            'member_role': member_role,
            'institution': institution, 
            'project': project, 
            'notices': notices, 
            'form': form,
            'formset': formset,
            'contributors': contributors,
        }
        return render(request, 'institutions/edit-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_others(request, pk, proj_id):
    institution = Institution.objects.select_related('institution_creator').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        project = Project.objects.prefetch_related('bc_labels', 'tk_labels', 'project_status').get(id=proj_id)
        entities_notified = EntitiesNotified.objects.get(project=project)
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
            title =  str(institution.institution_name) + ' has notified you of a Project.'

            for community_id in communities_selected:
                # Add communities that were notified to entities_notified instance
                community = Community.objects.get(id=community_id)
                entities_notified.communities.add(community)

                # Create project status, first comment and  notification
                ProjectStatus.objects.create(project=project, community=community, seen=False) # Creates a project status for each community
                if message:
                    ProjectComment.objects.create(project=project, community=community, sender=request.user, message=message)
                ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=reference_id, sender=request.user, title=title)
                entities_notified.save()

                # Create email 
                send_email_notice_placed(project, community, institution)
            
            return redirect('institution-projects', institution.id)

        context = {
            'institution': institution,
            'project': project,
            'communities': communities,
            'member_role': member_role,
        }
        return render(request, 'institutions/notify.html', context)

@login_required(login_url='login')
def connections(request, pk):
    institution = Institution.objects.select_related('institution_creator').get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return redirect('restricted')
    else:
        # TODO: figure out if this is needed
        # institution_ids = list(chain(
        #     institution.contributing_institutions.exclude(institutions__id=None).values_list('institutions__id', flat=True),
        # ))

        # researcher_ids = list(chain(
        #     institution.contributing_institutions.exclude(researchers__id=None).values_list('researchers__id', flat=True),
        # ))

        community_ids = list(chain(
            institution.contributing_institutions.exclude(communities__id=None).values_list('communities__id', flat=True),
        ))
        communities = Community.objects.select_related('community_creator').filter(id__in=community_ids)
        # institutions = Institution.objects.select_related('institution_creator').filter(id__in=institution_ids)
        # researchers = Researcher.objects.select_related('user').filter(id__in=researcher_ids)
            
        context = {
            'member_role': member_role,
            'institution': institution,
            'communities': communities,
            # 'researchers': researchers,
            # 'institutions': institutions
        }
        return render(request, 'institutions/connections.html', context)
