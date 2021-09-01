from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .utils import check_member_role
from projects.utils import add_to_contributors
from helpers.utils import set_notice_defaults

from .models import Institution
from researchers.models import Researcher
from projects.models import Project, ProjectContributors, ProjectPerson
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from helpers.models import ProjectComment, ProjectStatus, Notice, EntitiesNotified

from accounts.models import UserAffiliation

from projects.forms import CreateProjectForm, ProjectPersonFormset, EditProjectForm
from helpers.forms import ProjectCommentForm
from communities.forms import InviteMemberForm, JoinRequestForm
from .forms import CreateInstitutionForm, UpdateInstitutionForm, CreateInstitutionNoRorForm

@login_required(login_url='login')
def connect_institution(request):
    institutions = Institution.objects.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        institution_name = request.POST.get('organization_name')
        institution = Institution.objects.get(institution_name=institution_name)

        data = form.save(commit=False)
        data.user_from = request.user
        data.institution = institution
        data.user_to = institution.institution_creator
        data.save()
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
                data.is_approved = True
                data.save()
                return redirect('dashboard')
    return render(request, 'institutions/create-institution.html', {'form': form})

@login_required(login_url='login')
def create_institution_noror(request):
    form = CreateInstitutionNoRorForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            data = form.save(commit=False)
            data.institution_creator = request.user
            data.is_ror = False
            data.is_approved = False
            data.save()

            template = render_to_string('snippets/institution-application.html', { 'data' : data })
            send_mail(
                'New Institution Application', 
                template, 
                settings.EMAIL_HOST_USER, 
                [settings.SITE_ADMIN_EMAIL], 
                fail_silently=False)
        
            return redirect('dashboard')
    return render(request, 'institutions/create-institution-noror.html', {'form': form,})

# Update institution
@login_required(login_url='login')
def update_institution(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
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

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        return render(request, 'institutions/notices.html', {'institution': institution, 'member_role': member_role,})

# Members
@login_required(login_url='login')
def institution_members(request, pk):
    institution = Institution.objects.get(id=pk)
    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        return render(request, 'institutions/members.html', {'institution': institution, 'member_role': member_role,})

@login_required(login_url='login')
def add_member(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        form = InviteMemberForm(request.POST or None)
        if request.method == 'POST':
            receiver = request.POST.get('receiver')
            if form.is_valid():
                data = form.save(commit=False)
                data.sender = request.user
                data.status = 'sent'
                data.institution = institution
                data.save()
                messages.add_message(request, messages.INFO, 'Invitation Sent!')
                return render(request, 'institutions/add-member.html', {'institution': institution, 'form': form,})
            
        return render(request, 'institutions/add-member.html', {'institution': institution, 'form': form,})

# Projects
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
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
                    project = Project.objects.get(id=project_uuid)
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

    member_role = check_member_role(request.user, institution)
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
                add_to_contributors(contributors, data, institutions_selected, researchers_selected)

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

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / is a viewer.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        form = EditProjectForm(request.POST or None, instance=project)

        if request.method == 'POST':
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
        context = {
            'member_role': member_role,
            'institution': institution, 
            'project': project, 
            'form': form,
        }
        return render(request, 'institutions/edit-project.html', context)

# Notify Communities of Project
@login_required(login_url='login')
def notify_communities(request, pk, proj_id):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        project = Project.objects.get(id=proj_id)
        # notice_exists = project.project_notice.all().exists()
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
                    for notice in notices:
                        notice_status = ProjectStatus.objects.create(community=community, seen=False) # Creates a notice status for each community
                        notice.communities.add(community)
                        notice.save()

                        # Create notice status
                        notice_status.notice = notice
                        notice_status.save()

                        # Create first comment for notice
                        ProjectComment.objects.create(notice=notice, community=community, sender=request.user, message=message)

                        # Create notification
                        reference_id = str(notice.id)
                        title =  "A Notice has been placed by " + str(institution.institution_name) + '.'
                        ActionNotification.objects.create(community=community, notification_type='Project', reference_id=reference_id, sender=request.user, title=title)
            
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



