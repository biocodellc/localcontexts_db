from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .utils import *
from projects.utils import add_to_contributors
from helpers.utils import set_notice_defaults, dev_prod_or_local, create_notices

from .models import *
from projects.models import Project, ProjectContributors, ProjectPerson
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from helpers.models import ProjectComment, ProjectStatus, Notice, InstitutionNotice, EntitiesNotified, Connections

from django.contrib.auth.models import User
from accounts.models import UserAffiliation

from projects.forms import *
from helpers.forms import ProjectCommentForm
from communities.forms import InviteMemberForm, JoinRequestForm
from .forms import *

from helpers.emails import *

@login_required(login_url='login')
def connect_institution(request):
    institutions = Institution.objects.filter(is_approved=True)
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
                data = form.save(commit=False)
                data.user_from = request.user
                data.institution = institution
                data.user_to = institution.institution_creator
                data.save()

                # Send institution creator email
                send_join_request_email_admin(request.user, institution)
                return redirect('dashboard')
        else:
            messages.add_message(request, messages.ERROR, 'Institution not in registry')
            return redirect('connect-institution')

    context = { 'institutions': institutions, 'form': form,}
    return render(request, 'institutions/connect-institution.html', context)

@login_required(login_url='login')
def create_institution(request):
    form = CreateInstitutionForm(request.POST or None)
    if request.method == 'POST':
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
                    affiliation = UserAffiliation.objects.prefetch_related('institutions').get(user=request.user)
                    affiliation.institutions.add(data)
                    affiliation.save()

                    # Create a Connections instance
                    Connections.objects.create(institution=data)
                    return redirect('dashboard')
                else:
                    data.save()

                    # Add to user affiliations
                    affiliation = UserAffiliation.objects.prefetch_related('institutions').get(user=request.user)
                    affiliation.institutions.add(data)
                    affiliation.save()

                    # Create a Connections instance
                    Connections.objects.create(institution=data)
                    return redirect('confirm-institution', data.id)
    return render(request, 'institutions/create-institution.html', {'form': form})

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

                subject = ''
                if data.is_ror:
                    subject = 'New Institution Application: ' + str(data.institution_name)
                else:
                    subject = 'New Institution Application (non-ROR): ' + str(data.institution_name)

                send_hub_admins_application_email(institution, data, subject)
                return redirect('dashboard')
    return render(request, 'accounts/confirm-account.html', {'form': form, 'institution': institution,})


@login_required(login_url='login')
def create_institution_noror(request):
    form = CreateInstitutionNoRorForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            data = form.save(commit=False)
            data.institution_creator = request.user
            data.is_ror = False
            data.save()

            #  Create a Connections instance
            Connections.objects.create(institution=data)
        
            return redirect('confirm-institution', data.id)
    return render(request, 'institutions/create-institution-noror.html', {'form': form,})

# Update institution
@login_required(login_url='login')
def update_institution(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
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

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        return render(request, 'institutions/notices.html', {'institution': institution, 'member_role': member_role,})

# Members
@login_required(login_url='login')
def institution_members(request, pk):
    institution = Institution.objects.get(id=pk)
    member_role = check_member_role_institution(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        form = InviteMemberForm(request.POST or None)
        if request.method == 'POST':
            receiver = request.POST.get('receiver')
            user_in_institution = is_institution_in_user_institutions(receiver, institution)

            if user_in_institution == False: # If user is not an institution member
                check_invitation = does_institution_invite_exist(receiver, institution)

                if check_invitation == False: # If invitation does not exist, save form
                    if form.is_valid():
                        data = form.save(commit=False)
                        data.sender = request.user
                        data.status = 'sent'
                        data.institution = institution
                        data.save()
                        # Send email to target user
                        send_institution_invite_email(data, institution)
                        messages.add_message(request, messages.INFO, 'Invitation Sent!')
                        return redirect('institution-members', institution.id)
                else: 
                    messages.add_message(request, messages.INFO, 'This user has already been invited to this institution.')
            else:
                messages.add_message(request, messages.ERROR, 'This user is already a member of this institution.')

        context = { 
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }    
        return render(request, 'institutions/members.html', context)

    
@login_required(login_url='login')
def remove_member(request, pk, member_id):
    institution = Institution.objects.get(id=pk)
    member = User.objects.get(id=member_id)
    # what role does member have
    # remove from role
    if member in institution.admins.all():
        institution.admins.remove(member)
    if member in institution.editors.all():
        institution.editors.remove(member)
    if member in institution.viewers.all():
        institution.viewers.remove(member)

    # remove institution from userAffiloiation instance
    affiliation = UserAffiliation.objects.get(user=member)
    affiliation.institutions.remove(institution)
    return redirect('institution-members', institution.id)

# Projects
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        form = ProjectCommentForm(request.POST or None)
        institution_notified = EntitiesNotified.objects.filter(institutions=institution)
        
        if request.method == 'POST':
            project_uuid = request.POST.get('project-uuid')

            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if project_uuid:
                    project = Project.objects.get(unique_id=project_uuid)
                    data.project = project

                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-projects', institution.id)

        context = {
            'institution_notified': institution_notified,
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'institutions/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / is a viewer.
        return render(request, 'institutions/restricted.html', {'institution': institution})
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
                data.save()
                # Add project to institution projects
                institution.projects.add(data)

                #Create EntitiesNotified instance for the project
                EntitiesNotified.objects.create(project=data)

                # Create notices for project
                notices_selected = request.POST.getlist('checkbox-notice')
                create_notices(notices_selected, institution, data, None, None)

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                # Get project contributors instance and add institution
                contributors = ProjectContributors.objects.get(project=data)
                contributors.institutions.add(institution)
                # Add selected contributors to the ProjectContributors object
                add_to_contributors(contributors, institutions_selected, researchers_selected)

                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()

                # Format and send notification about the created project
                truncated_project_title = str(data.title)[0:30]
                title = 'A new project was created by ' + str(data.project_creator.get_full_name()) + ': ' + truncated_project_title
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
    notice_exists = Notice.objects.filter(project=project).exists()
    institution_notice_exists = InstitutionNotice.objects.filter(project=project).exists()

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / is a viewer.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        form = EditProjectForm(request.POST or None, instance=project)
        formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
        contributors = ProjectContributors.objects.get(project=project)


        if notice_exists:
            notice = Notice.objects.get(project=project)
        else:
            notice = None
        
        if institution_notice_exists:
            institution_notice = InstitutionNotice.objects.get(project=project)
        else:
            institution_notice = None

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
                add_to_contributors(contributors, institutions_selected, researchers_selected)

                # Which notices were selected to change
                notices_selected = request.POST.getlist('checkbox-notice')
                # Pass any existing notices as well as newly selected ones
                create_notices(notices_selected, institution, data, notice, institution_notice)

            return redirect('institution-projects', institution.id)

        context = {
            'member_role': member_role,
            'institution': institution, 
            'project': project, 
            'notice': notice, 
            'institution_notice': institution_notice,
            'form': form,
            'formset': formset,
            'contributors': contributors,
        }
        return render(request, 'institutions/edit-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_others(request, pk, proj_id):
    institution = Institution.objects.get(id=pk)
    project = Project.objects.get(id=proj_id)
    notice_exists = Notice.objects.filter(project=project).exists()
    institution_notice_exists = InstitutionNotice.objects.filter(project=project).exists()

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        communities = Community.objects.filter(is_approved=True)

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
                if notice_exists or institution_notice_exists:
                    # Add communities that were notified to entities_notified instance
                    entities_notified = EntitiesNotified.objects.get(project=project)
                    entities_notified.communities.add(community)
                    entities_notified.save()

                    # Create project status
                    project_status = ProjectStatus.objects.create(project=project, community=community, seen=False) # Creates a project status for each community
                    project_status.save()

                    # Create first comment for notice
                    ProjectComment.objects.create(project=project, community=community, sender=request.user, message=message)

                    # Create notification
                    reference_id = str(project.unique_id)
                    title =  "A Notice has been placed by " + str(institution.institution_name) + '.'
                    ActionNotification.objects.create(community=community, notification_type='Projects', reference_id=reference_id, sender=request.user, title=title)

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

def connections(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        connections = Connections.objects.get(institution=institution)
        context = {
            'member_role': member_role,
            'institution': institution,
            'connections': connections,
        }
        return render(request, 'institutions/connections.html', context)

def restricted_view(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/restricted.html', {'institution': institution, })



