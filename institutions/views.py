from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import check_member_role

from .models import Institution
from researchers.models import Researcher
from projects.models import Project, ProjectContributors
from bclabels.models import BCNotice, NoticeStatus
from tklabels.models import TKNotice
from communities.models import Community, JoinRequest
from notifications.models import ActionNotification
from accounts.models import UserAffiliation

from projects.forms import CreateProjectForm
from notifications.forms import NoticeCommentForm
from communities.forms import InviteMemberForm

from .forms import CreateInstitutionForm, UpdateInstitutionForm
# from bclabels.forms import AddBCNoticeMessage
# from tklabels.forms import AddTKNoticeMessage

@login_required(login_url='login')
def connect_institution(request):
    return render(request, 'institutions/connect-institution.html')

@login_required(login_url='login')
def create_institution(request):
    form = CreateInstitutionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            data = form.save(commit=False)
            data.institution_creator = request.user
            data.save()
            return redirect('dashboard')
    return render(request, 'institutions/create-institution.html', {'form': form})

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
        bcnotices = BCNotice.objects.filter(placed_by_institution=institution)
        tknotices = TKNotice.objects.filter(placed_by_institution=institution)

        if request.method == 'POST':
            project_id = request.POST.get('project-id')
            community_id = request.POST.get('community-id')
            project = Project.objects.get(id=project_id)
            community = Community.objects.get(id=community_id)

            form = NoticeCommentForm(request.POST or None)

            if form.is_valid():
                data = form.save(commit=False)
                data.project = project
                data.sender = request.user
                data.community = community
                data.save()
                return redirect('institution-activity', institution.id)
        else:
            form = NoticeCommentForm()

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
        if request.method == 'POST':
            form = InviteMemberForm(request.POST or None)
            receiver = request.POST.get('receiver')
            if form.is_valid():
                data = form.save(commit=False)
                data.sender = request.user
                data.status = 'sent'
                data.institution = institution
                data.save()
                messages.add_message(request, messages.INFO, 'Invitation Sent!')
                return render(request, 'institutions/add-member.html', {'institution': institution, 'form': form,})
        else:
            form = InviteMemberForm()
            
        return render(request, 'institutions/add-member.html', {'institution': institution, 'form': form,})

# Projects
@login_required(login_url='login')
def institution_projects(request, pk):
    institution = Institution.objects.get(id=pk)

    member_role = check_member_role(request.user, institution)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'institutions/restricted.html', {'institution': institution})
    else:
        contribs = ProjectContributors.objects.filter(institution=institution)
        context = {
            'institution': institution,
            'contribs': contribs,
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
        if request.method == "POST":
            form = CreateProjectForm(request.POST or None)
            if form.is_valid():
                data = form.save(commit=False)
                data.project_creator = request.user
                data.save()

                notices_selected = request.POST.getlist('checkbox-notice')

                for notice in notices_selected:
                    if notice == 'bcnotice':
                        bcnotice = BCNotice.objects.create(placed_by_institution=institution, project=data)
                    if notice == 'tknotice':
                        tknotice = TKNotice.objects.create(placed_by_institution=institution, project=data)

                ProjectContributors.objects.create(project=data, institution=institution)
                return redirect('institution-activity', institution.id)
        else:
            form = CreateProjectForm()

        context = {
            'institution': institution,
            'form': form,
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
        contribs = ProjectContributors.objects.get(project=project, institution=institution)

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
                        bcnotice.statuses.add(notice_status)
                        bcnotice.message = message
                        bcnotice.save()

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
                        tknotice.statuses.add(notice_status)
                        tknotice.message = message
                        tknotice.save()

                        # Create notification
                        reference_id = str(tknotice.unique_id)
                        title =  "A TK Notice has been placed by " + str(institution.institution_name) + '.'
                        ActionNotification.objects.create(community=community, notification_type='Activity', reference_id=reference_id, sender=request.user, title=title)

            
            return redirect('institution-projects', institution.id)

        context = {
            'institution': institution,
            'project': project,
            'contribs': contribs,
            'communities': communities,
            'member_role': member_role,
        }
        return render(request, 'institutions/notify.html', context)

def restricted_view(request, pk):
    institution = Institution.objects.get(id=pk)
    return render(request, 'institutions/restricted.html', {'institution': institution, })



