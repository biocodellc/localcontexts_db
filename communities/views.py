from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from mimetypes import guess_type

from django.contrib.auth.models import User
from accounts.models import UserAffiliation
from helpers.models import LabelTranslation, ProjectStatus, Notice, EntitiesNotified
from notifications.models import ActionNotification
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from projects.models import ProjectContributors, Project, ProjectPerson

from bclabels.forms import CustomizeBCLabelForm, ApproveAndEditBCLabelForm
from tklabels.forms import CustomizeTKLabelForm, ApproveAndEditTKLabelForm
from helpers.forms import AddLabelTranslationFormSet, UpdateBCLabelTranslationFormSet, UpdateTKLabelTranslationFormSet
from projects.forms import CreateProjectForm, ProjectPersonFormset, EditProjectForm
from helpers.forms import ProjectCommentForm

from bclabels.utils import check_bclabel_type, assign_bclabel_img
from tklabels.utils import check_tklabel_type, assign_tklabel_img
from projects.utils import add_to_contributors

from helpers.emails import send_email_with_attachment, send_simple_email

from .forms import *
from .models import *
from .utils import *

# Connect
@login_required(login_url='login')
def connect_community(request):
    communities = Community.objects.filter(is_approved=True)
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        community_id = request.POST.get('organization_name')
        community = Community.objects.get(community_name=community_id)

        data = form.save(commit=False)
        data.user_from = request.user
        data.community = community
        data.user_to = community.community_creator
        data.save()
        return redirect('dashboard')
    context = { 'communities': communities, 'form': form,}
    return render(request, 'communities/connect-community.html', context)

# Create Community
@login_required(login_url='login')
def create_community(request):
    form = CreateCommunityForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.community_creator = request.user
            data.save()
            return redirect('confirm-community', data.id)
    return render(request, 'communities/create-community.html', {'form': form})

# Confirm Community
@login_required(login_url='login')
def confirm_community(request, community_id):
    community = Community.objects.get(id=community_id)

    form = ConfirmCommunityForm(request.POST or None, request.FILES, instance=community)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.save()

            template = render_to_string('snippets/community-application.html', { 'data' : data })
        
            if request.FILES:
                uploaded_file = data.support_document
                send_email_with_attachment(uploaded_file, settings.SITE_ADMIN_EMAIL, 'New Community Application', template )
            else:
                send_simple_email(settings.SITE_ADMIN_EMAIL, 'New Community Application', template)

            return redirect('dashboard')
    return render(request, 'accounts/confirm-account.html', {'form': form, 'community': community,})

# Update Community / Settings
@login_required(login_url='login')
def update_community(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'editor' or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    
    else:
        update_form = UpdateCommunityForm(instance=community)
        if member_role == 'admin': # Only admins can change the form 
            if request.method == "POST":
                update_form = UpdateCommunityForm(request.POST, request.FILES, instance=community)
                if update_form.is_valid():
                    update_form.save()
                    messages.add_message(request, messages.SUCCESS, 'Updated!')
                    return redirect('update-community', community.id)
            else:
                update_form = UpdateCommunityForm(instance=community)

        context = {
            'community': community,
            'update_form': update_form,
            'member_role': member_role,
        }
        return render(request, 'communities/update-community.html', context)

# Members
@login_required(login_url='login')
def community_members(request, pk):
    community = Community.objects.get(id=pk)
    member_role = check_member_role(request.user, community)
    return render(request, 'communities/members.html', {'community': community, 'member_role': member_role, })

# Add member
@login_required(login_url='login')
def add_member(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})

    else:
        form = InviteMemberForm(request.POST or None)
        if request.method == "POST":
            receiver = request.POST.get('receiver')
            user_check = checkif_community_in_user_community(receiver, community)
            
            if user_check == False: # If user is not community member
                check_invitation = checkif_invite_exists(receiver, community) # Check to see if invitation already exists

                if check_invitation == False: # If invitation does not exist, save form.
                    if form.is_valid():
                        obj = form.save(commit=False)
                        obj.sender = request.user
                        obj.status = 'sent'
                        obj.community = community
                        obj.save()

                        messages.add_message(request, messages.INFO, 'Invitation Sent!')
                        return redirect('members', community.id)

                else: 
                    messages.add_message(request, messages.INFO, 'This user has already been invited to this community.')
                    return render(request, 'communities/add-member.html', {'community': community, 'form': form,})
            else:
                messages.add_message(request, messages.ERROR, 'This user is already a member.')
                return render(request, 'communities/add-member.html', {'community': community, 'form': form,})

        context = {
            'community': community,
            'form': form,
            'member_role': member_role,
        }
        return render(request, 'communities/add-member.html', context)

@login_required(login_url='login')
def remove_member(request, pk, member_id):
    community = Community.objects.get(id=pk)
    member = User.objects.get(id=member_id)
    # what role does member have
    # remove from role
    if member in community.admins.all():
        community.admins.remove(member)
    if member in community.editors.all():
        community.editors.remove(member)
    if member in community.viewers.all():
        community.viewers.remove(member)

    # remove community from userAffiloiation instance
    affiliation = UserAffiliation.objects.get(user=member)
    affiliation.communities.remove(community)
    return redirect('members', community.id)

# Select Labels to Customize
@login_required(login_url='login')
def select_label(request, pk):
    community = Community.objects.get(id=pk)
    bclabels = BCLabel.objects.filter(community=community)
    tklabels = TKLabel.objects.filter(community=community)


    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            bclabel_type = request.POST.get('bclabel-type')
            tklabel_type = request.POST.get('tk-label-type')
            
            # check if type already exists
            if bclabel_type:
                bctype = check_bclabel_type(bclabel_type)
                type_exists = BCLabel.objects.filter(community=community, label_type=bctype).exists()
                if type_exists:
                    return redirect('label-exists', community.id)
                else:
                    return redirect('customize-label', community.id, bclabel_type)

            if tklabel_type:
                tktype = check_tklabel_type(tklabel_type)
                type_exists = TKLabel.objects.filter(community=community, label_type=tktype).exists()
                if type_exists:
                    return redirect('label-exists', community.id)
                else:
                    return redirect('customize-label', community.id, tklabel_type)
        
        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
            'tklabels': tklabels,
        }

        return render(request, 'communities/select-label.html', context)

@login_required(login_url='login')
def label_exists(request, pk):
    community = Community.objects.get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {'community': community, 'member_role': member_role,}
        return render(request, 'communities/label-exists.html', context)

@login_required(login_url='login')
def customize_label(request, pk, label_type):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer':
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        # TK Label
        if label_type.startswith('tk'):
            tk_type = check_tklabel_type(label_type)
            img_url = assign_tklabel_img(label_type)

            form = CustomizeTKLabelForm(request.POST or None)

            if request.method == "GET":
                formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

            elif request.method == "POST":
                formset = AddLabelTranslationFormSet(request.POST)
                label_name = request.POST.get('input-label-name')

                if form.is_valid() and formset.is_valid():
                    label_form = form.save(commit=False)
                    label_form.name = label_name
                    label_form.label_type = tk_type
                    label_form.community = community
                    label_form.img_url = img_url
                    label_form.created_by = request.user
                    label_form.is_approved = False
                    label_form.save()

                    # Save all label translation instances
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.tklabel = label_form
                        instance.save()
                    
                    # Create notification
                    title = "A TK Label was customized by " + request.user.get_full_name() + " and is waiting approval by another member of the community."
                    ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                    return redirect('select-label', community.id)

        # BCLabel
        if label_type.startswith('bc'):
            bc_type = check_bclabel_type(label_type)
            img_url = assign_bclabel_img(label_type)

            form = CustomizeBCLabelForm(request.POST or None)

            if request.method == "GET":
                formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

            elif request.method == "POST":
                formset = AddLabelTranslationFormSet(request.POST)
                label_name = request.POST.get('input-label-name')

                if form.is_valid() and formset.is_valid():
                    label_form = form.save(commit=False)
                    label_form.name = label_name
                    label_form.label_type = bc_type
                    label_form.community = community
                    label_form.img_url = img_url
                    label_form.created_by = request.user
                    label_form.is_approved = False
                    label_form.save()

                    # Save all label translation instances
                    instances = formset.save(commit=False)
                    for instance in instances:
                        instance.bclabel = label_form
                        instance.save()

                    # Send notification
                    title = "A BC Label was customized by " + request.user.get_full_name() + " and is waiting approval by another member of the community."
                    ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                    return redirect('select-label', community.id)
            
        context = {
            'member_role': member_role,
            'community': community,
            'label_type': label_type,
            'form': form,
            'formset': formset,
        }
        return render(request, 'communities/customize-label.html', context)

@login_required(login_url='login')
def approve_label(request, pk, label_id):
    community = Community.objects.get(id=pk)
    bclabel_exists = BCLabel.objects.filter(unique_id=label_id).exists()
    tklabel_exists = TKLabel.objects.filter(unique_id=label_id).exists()

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer':
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        bclabel_name = ''
        tklabel_name = ''
        if bclabel_exists:
            bclabel = BCLabel.objects.get(unique_id=label_id)
            bclabel_name = bclabel.name
            form = ApproveAndEditBCLabelForm(request.POST or None, instance=bclabel)
            formset = UpdateBCLabelTranslationFormSet(request.POST or None, instance=bclabel)

        if tklabel_exists:
            tklabel = TKLabel.objects.get(unique_id=label_id)
            tklabel_name = tklabel.name
            form = ApproveAndEditTKLabelForm(request.POST or None, instance=tklabel)
            formset = UpdateTKLabelTranslationFormSet(request.POST or None, instance=tklabel)
        
        if request.method == "POST":
            if form.is_valid() and formset.is_valid():
                label_form = form.save(commit=False)
                label_form.is_approved = True
                label_form.approved_by = request.user
                label_form.save()

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.save()

                title = "A Label was approved by " + request.user.get_full_name()
                ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                return redirect('select-label', community.id)

        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'formset': formset,
            'tklabel_name': tklabel_name,
            'bclabel_name': bclabel_name,
        }
        return render(request, 'communities/approve-label.html', context)

# Projects Main
@login_required(login_url='login')
def projects(request, pk):
    community = Community.objects.get(id=pk)
    
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        community_notified = EntitiesNotified.objects.filter(communities=community)
        form = ProjectCommentForm(request.POST or None)

        # Form: Notify project contributor if project was seen
        if request.method == "POST" and "notify-btn" in request.POST:
            project_uuid = request.POST.get('project-uuid')

            if project_uuid != None and project_uuid != 'placeholder':
                project_status = request.POST.get('project-status')

                project = Project.objects.get(unique_id=project_uuid)
                reference_id = project.unique_id
                statuses = ProjectStatus.objects.filter(project=project, community=community)
                truncated_project_title = str(project.title)[0:30]

                for status in statuses:
                    if project_status == 'seen':
                        status.seen = True
                        status.save()

                        # Send Notification
                        title = community.community_name + ' has seen and acknowledged your Project: ' + truncated_project_title
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, institution=notice.placed_by_institution, notification_type='Projects', reference_id=reference_id)
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, researcher=notice.placed_by_researcher, notification_type='Projects', reference_id=reference_id)


                    if project_status == 'pending':
                        status.seen = True
                        status.status = 'pending'
                        status.save()

                        # Send Notification
                        title = community.community_name + ' is in the process of applying Labels to your Project: ' + truncated_project_title
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, institution=notice.placed_by_institution, notification_type='Projects', reference_id=reference_id)
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, researcher=notice.placed_by_researcher, notification_type='Projects', reference_id=reference_id)

                    if project_status == 'not_pending':
                        status.seen = True
                        status.status = 'not_pending'
                        status.save()
                       
                        # Send Notification
                        title = community.community_name + ' will not be applying Labels to your Project: ' + truncated_project_title
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, institution=notice.placed_by_institution, notification_type='Projects', reference_id=reference_id)
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, researcher=notice.placed_by_researcher, notification_type='Projects', reference_id=reference_id)
                        
                return redirect('community-projects', community.id)

        # Form: Add comment to notice
        elif request.method == "POST" and "add-comment-btn" in request.POST:
            project_id = request.POST.get('project-uuid')

            # Which project ?
            project_exists = Project.objects.filter(unique_id=project_id).exists()

            if project_exists:
                project = Project.objects.get(unique_id=project_id)
                status = ProjectStatus.objects.get(project=project, community=community)
                truncated_project_title = str(project.title)[0:30]

                if form.is_valid():
                    data = form.save(commit=False)
                    data.project = project
                    data.sender = request.user
                    data.community = community
                    data.save()

                    # If message is sent, set notice status to 'Seen'
                    if status.seen == False:
                        status.seen = True
                        status.save()

                        # Send Notification
                        title = community.community_name + ' has added a comment to your Project: ' + truncated_project_title
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, institution=notice.placed_by_institution, notification_type='Projects', reference_id=reference_id)
                        if project.project_notice.all():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, researcher=notice.placed_by_researcher, notification_type='Projects', reference_id=reference_id)


                    return redirect('community-projects', community.id)

        context = {
            'community_notified': community_notified,
            'community': community,
            'member_role': member_role,
            'form': form,
        }
        return render(request, 'communities/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    community = Community.objects.get(id=pk)

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "GET":
            form = CreateProjectForm(request.GET or None)
            formset = ProjectPersonFormset(queryset=ProjectPerson.objects.none())
        elif request.method == 'POST':
            form = CreateProjectForm(request.POST)
            formset = ProjectPersonFormset(request.POST)

            if form.is_valid() and formset.is_valid():
                data = form.save(commit=False)
                data.project_creator = request.user
                data.save()

                # Add project to community projects
                community.projects.add(data)

                #Create EntitiesNotified instance for the project
                EntitiesNotified.objects.create(project=data)

                # Get a project contrubutor object and add community to it.
                contributors = ProjectContributors.objects.get(project=data)
                contributors.communities.add(community)

                # Get lists of contributors entered in form
                institutions_selected = request.POST.getlist('selected_institutions')
                researchers_selected = request.POST.getlist('selected_researchers')

                add_to_contributors(contributors, data, institutions_selected, researchers_selected)
                
                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()

                # Send notification
                truncated_project_title = str(data.title)[0:30]
                title = 'A new project was created by ' + str(data.project_creator.get_full_name()) + ': ' + truncated_project_title + ' ...'
                ActionNotification.objects.create(title=title, sender=request.user, community=community, notification_type='Projects', reference_id=data.unique_id)
                return redirect('community-projects', community.id)
        
        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'formset': formset,
            'bclabels': bclabels,
            'tklabels': tklabels,
        }

        return render(request, 'communities/create-project.html', context)

@login_required(login_url='login')
def edit_project(request, community_id, project_uuid):
    community = Community.objects.get(id=community_id)
    project = Project.objects.get(unique_id=project_uuid)
    
    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = EditProjectForm(request.POST or None, instance=project)

        if request.method == 'POST':
            if form.is_valid():
                data = form.save(commit=False)
                data.save()

        context = {
            'member_role': member_role,
            'community': community, 
            'project': project, 
            'form': form,
        }
        return render(request, 'communities/edit-project.html', context)

@login_required(login_url='login')
def apply_labels(request, pk, project_uuid):
    community = Community.objects.get(id=pk)
    project = Project.objects.get(unique_id=project_uuid)
    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    notices = project.project_notice.all()

    # Define Notification attrs
    reference_id = str(project.unique_id)
    truncated_project_title = str(project.title)[0:30]
    title = community.community_name + ' has applied Labels to project ' + truncated_project_title + ' ...'

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
             # Set private project to discoverable
            if project.project_privacy == 'Private':
                project.project_privacy = 'Discoverable'
                project.save()

            # Get uuids of each label that was checked and add them to the project
            bclabels_selected = request.POST.getlist('selected_bclabels')
            tklabels_selected = request.POST.getlist('selected_tklabels')

            for bclabel_uuid in bclabels_selected:
                bclabel = BCLabel.objects.get(unique_id=bclabel_uuid)
                project.bc_labels.add(bclabel)

            for tklabel_uuid in tklabels_selected:
                tklabel = TKLabel.objects.get(unique_id=tklabel_uuid)
                project.tk_labels.add(tklabel)
            
            if notices:
                # add community to project contributors
                contributors = ProjectContributors.objects.get(project=project)
                contributors.communities.add(community)
                contributors.save()
            else:
                comm_title = 'Labels have been applied to the project ' + truncated_project_title + ' ...'
                ActionNotification.objects.create(title=comm_title, notification_type='Projects', community=community, reference_id=reference_id)

            # If BC Notice exists
            if notices:
                for n in notices:
                    # Archive notice
                    n.archived = True
                    n.save()
                    # send notification to either institution or researcher
                    if n.placed_by_institution:
                        ActionNotification.objects.create(title=title, institution=n.placed_by_institution, notification_type='Labels', reference_id=reference_id)
                    if n.placed_by_researcher:
                        ActionNotification.objects.create(title=title, researcher=n.placed_by_researcher, notification_type='Labels', reference_id=reference_id)

            return redirect('community-projects', community.id)

    context = {
        'community': community,
        'project': project,
        'bclabels': bclabels,
        'tklabels': tklabels,
    }
    return render(request, 'communities/apply-labels.html', context)

def restricted_view(request, pk):
    community = Community.objects.get(id=pk)
    return render(request, 'communities/restricted.html', {'community': community, })
