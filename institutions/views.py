from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.conf import settings
from django.template.loader import render_to_string

from .utils import *
from projects.utils import add_to_contributors
from helpers.utils import set_notice_defaults

from .models import *
from projects.models import Project, ProjectContributors, ProjectPerson
from communities.models import Community
from notifications.models import ActionNotification
from helpers.models import ProjectComment, ProjectStatus, Notice, EntitiesNotified

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
        institution = Institution.objects.get(institution_name=institution_name)

        data = form.save(commit=False)
        data.user_from = request.user
        data.institution = institution
        data.user_to = institution.institution_creator
        data.save()

        # Send institution creator email
        send_join_request_email_admin(request.user, institution)
        
        return redirect('dashboard')
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
                data.save()
                return redirect('confirm-institution', data.id)
    return render(request, 'institutions/create-institution.html', {'form': form})

@login_required(login_url='login')
def confirm_institution(request, institution_id):
    institution = Institution.objects.get(id=institution_id)

    form = ConfirmInstitutionForm(request.POST or None, request.FILES, instance=institution)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
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
        return render(request, 'institutions/members.html', {'institution': institution, 'member_role': member_role,})
    
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

@login_required(login_url='login')
def add_member(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role_institution(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
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
                    return render(request, 'institutions/add-member.html', {'institution': institution, 'form': form,})
            else:
                messages.add_message(request, messages.ERROR, 'This user is already a member of this institution.')
                return render(request, 'institutions/add-member.html', {'institution': institution, 'form': form,})


        context = { 
            'institution': institution,
            'form': form,
            'member_role': member_role,
        }    
        return render(request, 'institutions/add-member.html', context)

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

                # Create notice for project
                notices_selected = request.POST.getlist('checkbox-notice')
                if len(notices_selected) > 1:
                    notice = Notice.objects.create(notice_type='biocultural_and_traditional_knowledge', placed_by_institution=institution, project=data)
                    set_notice_defaults(notice)
                else:
                    for selected in notices_selected:
                        if selected == 'bcnotice':
                            notice = Notice.objects.create(notice_type='biocultural', placed_by_institution=institution, project=data)
                            set_notice_defaults(notice)
                        elif selected == 'tknotice':
                            notice = Notice.objects.create(notice_type='traditional_knowledge', placed_by_institution=institution, project=data)
                            set_notice_defaults(notice)

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
    notice_exists = Notice.objects.filter(project=project)

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
                # If both notices were selected, check to see if notice exists
                # If not, create new notice delete old one
                if len(notices_selected) > 1:
                    notice_exists_both = Notice.objects.filter(project=project, notice_type='biocultural_and_traditional_knowledge').exists()
                    if not notice_exists_both:
                        notice_both = Notice.objects.create(project=project, notice_type='biocultural_and_traditional_knowledge', placed_by_institution=institution)
                        set_notice_defaults(notice_both)
                        notice.delete()
                else:
                    # If one notice was selected, check if it already exists
                    # If not, create new notice, delete old one
                    for selected in notices_selected:
                        if selected == 'bcnotice':
                            notice_exists_bc = Notice.objects.filter(project=project, notice_type='biocultural').exists()
                            if not notice_exists_bc:
                                bc_notice = Notice.objects.create(project=project, notice_type='biocultural', placed_by_institution=institution)
                                set_notice_defaults(bc_notice)
                                notice.delete()

                        elif selected == 'tknotice':
                            notice_exists_tk = Notice.objects.filter(project=project, notice_type='traditional_knowledge').exists()
                            if not notice_exists_tk:
                                tk_notice = Notice.objects.create(project=project, notice_type='traditional_knowledge', placed_by_institution=institution)
                                set_notice_defaults(tk_notice)
                                notice.delete()

            return redirect('institution-projects', institution.id)

        context = {
            'member_role': member_role,
            'institution': institution, 
            'project': project, 
            'notice': notice, 
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
    notice_exists = Notice.objects.filter(project=project)

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
                if notice_exists:
                    notices = Notice.objects.filter(project=project)
                    for notice in notices:
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
            
            return redirect('institution-projects', institution.id)

        context = {
            'institution': institution,
            'project': project,
            'communities': communities,
            'member_role': member_role,
        }
        return render(request, 'institutions/notify.html', context)

def restricted_view(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/restricted.html', {'institution': institution, })



