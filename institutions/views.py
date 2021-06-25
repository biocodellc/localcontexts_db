from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .utils import check_member_role
from projects.utils import add_to_contributors

from .models import Institution
from researchers.models import Researcher
from projects.models import Project, ProjectContributors, ProjectPerson
from bclabels.models import BCNotice
from tklabels.models import TKNotice
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification, NoticeComment, NoticeStatus
from accounts.models import UserAffiliation

from projects.forms import CreateProjectForm, ProjectPersonFormset
from notifications.forms import NoticeCommentForm
from communities.forms import InviteMemberForm, JoinRequestForm
from .forms import CreateInstitutionForm, UpdateInstitutionForm, CreateInstitutionNoRorForm

@login_required(login_url='login')
def connect_institution(request):
    institutions = Institution.objects.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        institution_id = request.POST.get('organization_name')
        institution = Institution.objects.get(institution_name=institution_id)

        data = form.save(commit=False)
        data.user_from = request.user
        data.institution = institution
        data.user_to = institution.institution_creator
        data.save()
        # Create a notification here
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

# Registry
def institution_registry(request):
    institutions = Institution.objects.all()

    if request.user.is_authenticated:
        current_user = UserAffiliation.objects.get(user=request.user)
        user_institutions = current_user.institutions.all()

        if request.method == 'POST':
            buttonid = request.POST.get('instid')
            target_institution = Institution.objects.get(id=buttonid)
            main_admin = target_institution.institution_creator

            join_request = JoinRequest.objects.create(user_from=request.user, institution=target_institution, user_to=main_admin)
            join_request.save()
            return redirect('institution-registry')
    else:
        return render(request, 'institutions/institution-registry.html', {'institutions': institutions})

    context = {
        'institutions': institutions,
        'user_institutions': user_institutions,
    }
    return render(request, 'institutions/institution-registry.html', context)


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

# Activity
@login_required(login_url='login')
def institution_activity(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        form = NoticeCommentForm(request.POST or None)
        bcnotices = BCNotice.objects.filter(placed_by_institution=institution)
        tknotices = TKNotice.objects.filter(placed_by_institution=institution)

        if request.method == 'POST':
            bcnotice_uuid = request.POST.get('bcnotice-uuid')
            tknotice_uuid = request.POST.get('tknotice-uuid')

            community_id = request.POST.get('community-id')
            community = Community.objects.get(id=community_id)

            if form.is_valid():
                data = form.save(commit=False)

                if bcnotice_uuid:
                    bcnotice = BCNotice.objects.get(unique_id=bcnotice_uuid)
                    data.bcnotice = bcnotice
                else:
                    tknotice = TKNotice.objects.get(unique_id=tknotice_uuid)
                    data.tknotice = tknotice

                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-activity', institution.id)

        context = {
            'institution': institution,
            'bcnotices': bcnotices,
            'tknotices': tknotices,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'institutions/activity.html', context)

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
        context = {
            'institution': institution,
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

                notices_selected = request.POST.getlist('checkbox-notice')
                for notice in notices_selected:
                    if notice == 'bcnotice':
                        bcnotice = BCNotice.objects.create(placed_by_institution=institution, project=data)
                    if notice == 'tknotice':
                        tknotice = TKNotice.objects.create(placed_by_institution=institution, project=data)

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

# Notify Communities of Project
@login_required(login_url='login')
def notify_communities(request, pk, proj_id):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        project = Project.objects.get(id=proj_id)

        bcnotice_exists = BCNotice.objects.filter(project=project).exists()
        tknotice_exists = TKNotice.objects.filter(project=project).exists()

        communities = Community.objects.all()

        if request.method == "POST":
            communities_selected = request.POST.getlist('selected_communities')
            message = request.POST.get('notice_message')

            for community_id in communities_selected:
                community = Community.objects.get(id=community_id)
                
                # add community to bcnotice instance
                if bcnotice_exists:
                    bcnotices = BCNotice.objects.filter(project=project)
                    notice_status = NoticeStatus.objects.create(community=community, seen=False) # Creates a notice status for each community
                    for bcnotice in bcnotices:
                        bcnotice.communities.add(community)
                        bcnotice.save()

                        # Create notice status
                        notice_status.bcnotice = bcnotice
                        notice_status.save()

                        # Create first comment for notice
                        NoticeComment.objects.create(bcnotice=bcnotice, community=community, sender=request.user, message=message)

                        # Create notification
                        reference_id = str(bcnotice.unique_id)
                        title =  "A BC Notice has been placed by " + str(institution.institution_name) + '.'
                        ActionNotification.objects.create(community=community, notification_type='Activity', reference_id=reference_id, sender=request.user, title=title)
                
                # add community to tknotice instance
                if tknotice_exists:
                    tknotices = TKNotice.objects.filter(project=project)
                    notice_status = NoticeStatus.objects.create(community=community, seen=False)
                    for tknotice in tknotices:
                        tknotice.communities.add(community)
                        tknotice.save()

                        # Create notice status
                        notice_status.tknotice = tknotice
                        notice_status.save()

                        # Create first comment for notice
                        NoticeComment.objects.create(tknotice=tknotice, community=community, sender=request.user, message=message)

                        # Create notification
                        reference_id = str(tknotice.unique_id)
                        title =  "A TK Notice has been placed by " + str(institution.institution_name) + '.'
                        ActionNotification.objects.create(community=community, notification_type='Activity', reference_id=reference_id, sender=request.user, title=title)

            
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



