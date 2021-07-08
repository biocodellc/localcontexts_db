from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string

from mimetypes import guess_type

from accounts.models import UserAffiliation
from helpers.models import LabelTranslation
from notifications.models import ActionNotification, NoticeStatus
from bclabels.models import BCNotice, BCLabel
from tklabels.models import TKNotice, TKLabel
from projects.models import ProjectContributors, Project, ProjectPerson

from bclabels.forms import CustomiseBCLabelForm, ApproveAndEditBCLabelForm
from tklabels.forms import CustomiseTKLabelForm, ApproveAndEditTKLabelForm
from helpers.forms import AddLabelTranslationFormSet, UpdateBCLabelTranslationFormSet, UpdateTKLabelTranslationFormSet
from projects.forms import CreateProjectForm, ProjectPersonFormset
from notifications.forms import NoticeCommentForm

from bclabels.utils import check_bclabel_type
from tklabels.utils import check_tklabel_type
from projects.utils import add_to_contributors

from .forms import *
from .models import *
from .utils import *

# Connect
@login_required(login_url='login')
def connect_community(request):
    communities = Community.objects.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        community_id = request.POST.get('organization_name')
        community = Community.objects.get(community_name=community_id)

        data = form.save(commit=False)
        data.user_from = request.user
        data.community = community
        data.user_to = community.community_creator
        data.save()
        # Create a notification here
        return redirect('dashboard')
    context = { 'communities': communities, 'form': form,}
    return render(request, 'communities/connect-community.html', context)

# Create Community
@login_required(login_url='login')
def create_community(request):
    form = CreateCommunityForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.community_creator = request.user
            obj.save()
            return redirect('validate-community', obj.id)
    return render(request, 'communities/create-community.html', {'form': form})

# Validate Community
@login_required(login_url='login')
def validate_community(request, community_id):
    community = Community.objects.get(id=community_id)

    form = ValidateCommunityForm(request.POST or None, request.FILES, instance=community)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()

            # https://docs.djangoproject.com/en/dev/topics/email/#the-emailmessage-class
            template = render_to_string('snippets/community-application.html', { 'obj' : obj })

            email = EmailMessage(
                'New Community Application',
                template,
                settings.EMAIL_HOST_USER, 
                [settings.SITE_ADMIN_EMAIL], 
            )
            if request.FILES:
                uploaded_file = obj.support_document
                file_type = guess_type(uploaded_file.name)
                email.attach(uploaded_file.name, uploaded_file.read(), file_type[0])
            email.send()

            return redirect('dashboard')
    return render(request, 'communities/validate-community.html', {'form': form})

# Registry
def community_registry(request):
    communities = Community.objects.filter(is_approved=True, is_publicly_listed=True)

    if request.user.is_authenticated:
        current_user = UserAffiliation.objects.get(user=request.user)
        user_communities = current_user.communities.all()

        if request.method == 'POST':
            buttonid = request.POST.get('commid')
            target_community = Community.objects.get(id=buttonid)
            main_admin = target_community.community_creator

            req = JoinRequest.objects.create(user_from=request.user, community=target_community, user_to=main_admin)
            req.save()

            return redirect('community-registry')
    else:
        return render(request, 'communities/community-registry.html', {'communities': communities})

    context = {
        'communities': communities,
        'user_communities': user_communities,
    }
    return render(request, 'communities/community-registry.html', context)

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

# Activity / Notices
@login_required(login_url='login')
def community_activity(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        bcnotices = BCNotice.objects.filter(communities=community)
        tknotices = TKNotice.objects.filter(communities=community)

        # Form: Notify project contributor if notice was seen
        if request.method == "POST" and "notify-btn" in request.POST:
            bcnotice_uuid = request.POST.get('bcnotice-uuid')
            tknotice_uuid = request.POST.get('tknotice-uuid')

            if bcnotice_uuid != None and bcnotice_uuid != 'placeholder':
                bcnotice_status = request.POST.get('bcnotice-status')

                bcnotice = BCNotice.objects.get(unique_id=bcnotice_uuid)
                reference_id = str(bcnotice.unique_id)
                statuses = NoticeStatus.objects.filter(bcnotice=bcnotice, community=community)

                for status in statuses:
                    if bcnotice_status == 'seen':
                        status.seen = True
                        status.save()

                    if bcnotice_status == 'pending':
                        status.seen = True
                        status.status = 'pending'
                        status.save()

                        truncated_project_title = str(bcnotice.project.title)[0:30]
                        title = community.community_name + ' is in the process of applying Labels to your BC Notice: ' + truncated_project_title
                        if bcnotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=bcnotice.placed_by_institution, notification_type='Activity', reference_id=reference_id)
                        if bcnotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=bcnotice.placed_by_researcher, notification_type='Activity', reference_id=reference_id)

                    if bcnotice_status == 'not_pending':
                        status.seen = True
                        status.status = 'not_pending'
                        status.save()

                        truncated_project_title = str(bcnotice.project.title)[0:30]
                        title = community.community_name + ' will not be applying Labels to your BC Notice: ' + truncated_project_title
                        if bcnotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=bcnotice.placed_by_institution, notification_type='Activity', reference_id=reference_id)
                        if bcnotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=bcnotice.placed_by_researcher, notification_type='Activity', reference_id=reference_id)
                        
                return redirect('community-activity', community.id)

            if tknotice_uuid != None and tknotice_uuid != 'placeholder':
                tknotice_status = request.POST.get('tknotice-status')

                tknotice = TKNotice.objects.get(unique_id=tknotice_uuid)
                reference_id = str(tknotice.unique_id)
                statuses = NoticeStatus.objects.filter(tknotice=tknotice, community=community)

                for status in statuses:
                    if tknotice_status == 'seen':
                        status.seen = True
                        status.save()

                    if tknotice_status == 'pending':
                        status.seen = True
                        status.status = 'pending'
                        status.save()

                        truncated_project_title = str(tknotice.project.title)[0:30]
                        title = community.community_name + ' is in the process of applying Labels to your TK Notice: ' + truncated_project_title
                        if tknotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=tknotice.placed_by_institution, notification_type='Activity', reference_id=reference_id)
                        if tknotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=tknotice.placed_by_researcher, notification_type='Activity', reference_id=reference_id)

                    if tknotice_status == 'not_pending':
                        status.seen = True
                        status.status = 'not_pending'
                        status.save()
                        
                        truncated_project_title = str(tknotice.project.title)[0:30]
                        title = community.community_name + ' will not be applying Labels to your TK Notice: ' + truncated_project_title
                        if tknotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=tknotice.placed_by_institution, notification_type='Activity', reference_id=reference_id)
                        if tknotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=tknotice.placed_by_researcher, notification_type='Activity', reference_id=reference_id)

                return redirect('community-activity', community.id)

        # Form: Add comment to notice
        elif request.method == "POST" and "add-comment-btn" in request.POST:
            bcnotice_uuid = request.POST.get('bcnotice-uuid')
            tknotice_uuid = request.POST.get('tknotice-uuid')

            # Which notice ?
            bcnotice_exists = BCNotice.objects.filter(unique_id=bcnotice_uuid).exists()
            tknotice_exists = TKNotice.objects.filter(unique_id=tknotice_uuid).exists()

            form = NoticeCommentForm(request.POST or None)

            if bcnotice_exists:
                bcnotice = BCNotice.objects.get(unique_id=bcnotice_uuid)
                if form.is_valid():
                    data = form.save(commit=False)
                    data.bcnotice = bcnotice
                    data.sender = request.user
                    data.community = community
                    data.save()
                    return redirect('community-activity', community.id)
            
            if tknotice_exists:
                tknotice = TKNotice.objects.get(unique_id=tknotice_uuid)
                if form.is_valid():
                    data = form.save(commit=False)
                    data.tknotice = tknotice
                    data.sender = request.user
                    data.community = community
                    data.save()
                    return redirect('community-activity', community.id)

        else:
            form = NoticeCommentForm()

            context = {
                'bcnotices': bcnotices,
                'tknotices': tknotices,
                'community': community,
                'member_role': member_role,
                'form': form,
            }
            return render(request, 'communities/activity.html', context)

# Labels Main
@login_required(login_url='login')
def community_labels(request, pk):
    community = Community.objects.get(id=pk)
    bclabels = BCLabel.objects.filter(community=community)
    tklabels = TKLabel.objects.filter(community=community)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
            'tklabels': tklabels,
        }
        return render(request, 'communities/labels.html', context)

# Select Labels to Customise
@login_required(login_url='login')
def select_label(request, pk):
    community = Community.objects.get(id=pk)

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
                    return redirect('customise-bclabel', community.id, bclabel_type)

            if tklabel_type:
                tktype = check_tklabel_type(tklabel_type)
                type_exists = TKLabel.objects.filter(community=community, label_type=tktype).exists()
                if type_exists:
                    return redirect('label-exists', community.id)
                else:
                    return redirect('customise-tklabel', community.id, tklabel_type)
        
        context = {
            'community': community,
            'member_role': member_role,
        }

        return render(request, 'communities/select-label.html', context)

@login_required(login_url='login')
def label_exists(request, pk):
    community = Community.objects.get(id=pk)
    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'member_role': member_role,
        }
        return render(request, 'communities/label-exists.html', context)

# BC Label customisation process
@login_required(login_url='login')
def customise_bclabel(request, pk, label_type):
    community = Community.objects.get(id=pk)
    bc_type = check_bclabel_type(label_type)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = CustomiseBCLabelForm(request.POST or None)

        if request.method == "GET":
            formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

        elif request.method == "POST":
            formset = AddLabelTranslationFormSet(request.POST)

            if form.is_valid() and formset.is_valid():
                label_form = form.save(commit=False)
                label_form.label_type = bc_type
                label_form.community = community
                label_form.created_by = request.user
                label_form.is_approved = False
                label_form.save()

                # Save all label translation instances
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.bclabel = label_form
                    instance.save()

                title = "A BC Label was customised by " + request.user.get_full_name()
                ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                return redirect('community-labels', community.id)

        context = {
            'member_role': member_role,
            'community': community,
            'label_type': label_type,
            'form': form,
            'formset': formset,
        }
        return render(request, 'communities/customise-bclabel.html', context)

# TK Label customisation process
@login_required(login_url='login')
def customise_tklabel(request, pk, label_type):
    community = Community.objects.get(id=pk)
    tk_type = check_tklabel_type(label_type)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = CustomiseTKLabelForm(request.POST or None)

        if request.method == "GET":
            formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

        elif request.method == "POST":
            formset = AddLabelTranslationFormSet(request.POST)

            if form.is_valid() and formset.is_valid():
                label_form = form.save(commit=False)
                label_form.label_type = tk_type
                label_form.community = community
                label_form.created_by = request.user
                label_form.is_approved = False
                label_form.save()

                # Save all label translation instances
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.tklabel = label_form
                    instance.save()
                
                title = "A TK Label was customised by " + request.user.get_full_name() + " and is waiting approval by another member of the community."
                ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                return redirect('community-labels', community.id)

        context = {
            'community': community,
            'label_type': label_type,
            'form': form,
            'member_role': member_role,
            'formset': formset,
        }
        return render(request, 'communities/customise-tklabel.html', context)

# Approve BC Label
@login_required(login_url='login')
def approve_bclabel(request, pk, label_id):
    community = Community.objects.get(id=pk)
    bclabel = BCLabel.objects.get(unique_id=label_id)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer':
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = ApproveAndEditBCLabelForm(request.POST or None, instance=bclabel)
        formset = UpdateBCLabelTranslationFormSet(request.POST or None, instance=bclabel)

        if request.method == "POST":
            if form.is_valid() and formset.is_valid():
                label_form = form.save(commit=False)
                label_form.is_approved = True
                label_form.approved_by = request.user
                label_form.save()

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.save()

                title = "A BC Label was approved by " + request.user.get_full_name()
                ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)
                
                return redirect('community-labels', community.id)

        context = {
            'community': community,
            'bclabel': bclabel,
            'member_role': member_role,
            'form': form,
            'formset': formset,
        }
        return render(request, 'communities/approve-bclabel.html', context)

# Approve TK Labels
@login_required(login_url='login')
def approve_tklabel(request, pk, label_id):
    community = Community.objects.get(id=pk)
    tklabel = TKLabel.objects.get(unique_id=label_id)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer':
        return render(request, 'communities/restricted.html', {'community': community})
    else:
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

                title = "A TK Label was approved by " + request.user.get_full_name()
                ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                return redirect('community-labels', community.id)

        context = {
            'community': community,
            'tklabel': tklabel,
            'member_role': member_role,
            'form': form,
            'formset': formset,
        }
        return render(request, 'communities/approve-tklabel.html', context)

# Projects Main
@login_required(login_url='login')
def projects(request, pk):
    community = Community.objects.get(id=pk)
    
    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community, 
            'member_role': member_role,
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

                # Maybe there's a better way to do this? using project unique id instead of contrib id?
                # Has to be a contrib id for the js to work. Rework this maybe?
                # contrib = ProjectContributors.objects.get(project=data)
                truncated_project_title = str(data.title)[0:30]
                title = 'A new project was created by ' + str(data.project_creator.get_full_name()) + ': ' + truncated_project_title + ' ...'
                # ActionNotification.objects.create(reference_id=contrib.id, title=title, sender=request.user, community=community, notification_type='Projects')
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

# Add labels to community created projects
@login_required(login_url='login')
def apply_project_labels(request, pk, project_id):
    community = Community.objects.get(id=pk)
    project = Project.objects.get(id=project_id)

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            # Get which labels were selected to be applied
            bclabels_selected = request.POST.getlist('checked-labels')
            tklabels_selected = request.POST.getlist('tk-checked-labels')

            for choice in bclabels_selected:
                label = BCLabel.objects.get(unique_id=choice)
                project.bclabels.add(label)
                #TODO: Create ActionNotification: tk label has been applied to project
                
            for tkchoice in tklabels_selected:
                tklabel = TKLabel.objects.get(unique_id=tkchoice)
                project.tklabels.add(tklabel)
                #TODO: Create ActionNotification: tk label has been applied to project
            
            return redirect('community-projects', community.id)

        context = {
            'community': community,
            'project': project,
            'bclabels': bclabels,
            'tklabels': tklabels,
            'member_role': member_role, 
        }
        return render(request, 'communities/apply-labels.html', context)

# Appy Labels to Notices
@login_required(login_url='login')
def apply_notice_labels(request, pk, notice_id):
    community = Community.objects.get(id=pk)

    bcnotice_exists = BCNotice.objects.filter(unique_id=notice_id).exists()
    tknotice_exists = TKNotice.objects.filter(unique_id=notice_id).exists()

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if bcnotice_exists:
            bcnotice = BCNotice.objects.get(unique_id=notice_id)
            if request.method == "POST":
                # add community to project contributors
                contributors = ProjectContributors.objects.get(project=bcnotice.project)
                contributors.communities.add(community)
                contributors.save()

                # Gets ids of all checkboxes
                label_selected = request.POST.getlist('checkbox-label')

                for choice in label_selected:
                    bclabel_exists = BCLabel.objects.filter(unique_id=choice).exists()
                    tklabel_exists = TKLabel.objects.filter(unique_id=choice).exists()

                    if bclabel_exists:
                        bclabel = BCLabel.objects.get(unique_id=choice)
                        bcnotice.project.bclabels.add(bclabel)
                        reference_id = str(bcnotice.project.unique_id)

                        truncated_project_title = str(bcnotice.project.title)[0:30]
                        title = community.community_name + ' has applied the ' + bclabel.name + ' Label to your project: ' + truncated_project_title + ' ...'

                        if bcnotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=bcnotice.placed_by_institution, notification_type='Labels', reference_id=reference_id)
                        if bcnotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=bcnotice.placed_by_researcher, notification_type='Labels', reference_id=reference_id)

                    if tklabel_exists:
                        tklabel = TKLabel.objects.get(unique_id=choice)
                        bcnotice.project.tklabels.add(tklabel)
                        reference_id = str(bcnotice.project.unique_id)

                        truncated_project_title = str(bcnotice.project.title)[0:30]
                        title = community.community_name + ' has applied the ' + tklabel.name + ' Label to your project ' + truncated_project_title + ' ...'

                        if bcnotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=bcnotice.placed_by_institution, notification_type='Labels', reference_id=reference_id)
                        if bcnotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=bcnotice.placed_by_researcher, notification_type='Labels', reference_id=reference_id)

                return redirect('community-projects', community.id)
            
            context = {
                'community': community,
                'bcnotice': bcnotice,
                'bclabels': bclabels,
                'tklabels': tklabels,
                'member_role': member_role,  
            }
            return render(request, 'communities/apply-notice-labels.html', context)

        else:
            tknotice = TKNotice.objects.get(unique_id=notice_id)
            if request.method == "POST":
                # add community to project contributors
                contrib = ProjectContributors.objects.get(project=tknotice.project)
                contrib.community = community
                contrib.save()

                # Gets ids of all checkboxes
                label_selected = request.POST.getlist('checkbox-label')

                for choice in label_selected:
                    bclabel_exists = BCLabel.objects.filter(unique_id=choice).exists()
                    tklabel_exists = TKLabel.objects.filter(unique_id=choice).exists()

                    if bclabel_exists:
                        bclabel = BCLabel.objects.get(unique_id=choice)
                        tknotice.project.bclabels.add(bclabel)
                        reference_id = str(tknotice.project.unique_id)

                        truncated_project_title = str(tknotice.project.title)[0:30]
                        title = community.community_name + ' has applied the ' + bclabel.name + ' Label to your project ' + truncated_project_title
                        if tknotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=tknotice.placed_by_institution, notification_type='Labels', reference_id=reference_id)
                        if tknotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=tknotice.placed_by_researcher, notification_type='Labels', reference_id=reference_id)

                    if tklabel_exists:
                        tklabel = TKLabel.objects.get(unique_id=choice)
                        tknotice.project.tklabels.add(tklabel)
                        reference_id = str(tknotice.project.unique_id)

                        truncated_project_title = str(tknotice.project.title)[0:30]
                        title = community.community_name + ' has applied the ' + tklabel.name + ' Label to your project ' + truncated_project_title
                        if tknotice.placed_by_institution:
                            ActionNotification.objects.create(title=title, institution=tknotice.placed_by_institution, notification_type='Labels', reference_id=reference_id)
                        if tknotice.placed_by_researcher:
                            ActionNotification.objects.create(title=title, researcher=tknotice.placed_by_researcher, notification_type='Labels', reference_id=reference_id)


                return redirect('community-projects', community.id)
        
            context = {
                'community': community,
                'tknotice': tknotice,
                'bclabels': bclabels,
                'tklabels': tklabels,
                'member_role': member_role,
            }
            return render(request, 'communities/apply-notice-labels.html', context)

# Relationships
@login_required(login_url='login')
def community_relationships(request, pk):
    community = Community.objects.get(id=pk)

    member_role = check_member_role(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        context = {
            'community': community,
            'member_role': member_role, 
        }
        return render(request, 'communities/relationships.html', context)

def restricted_view(request, pk):
    community = Community.objects.get(id=pk)

    return render(request, 'communities/restricted.html', {'community': community, })
