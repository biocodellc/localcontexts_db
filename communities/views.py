from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User
from accounts.models import UserAffiliation
from helpers.models import LabelTranslation, ProjectStatus, EntitiesNotified, Connections
from notifications.models import ActionNotification
from bclabels.models import BCLabel
from tklabels.models import TKLabel
from projects.models import ProjectContributors, Project, ProjectPerson

from helpers.forms import AddLabelTranslationFormSet, LabelNoteForm, ProjectCommentForm, UpdateBCLabelTranslationFormSet, UpdateTKLabelTranslationFormSet
from bclabels.forms import *
from tklabels.forms import *
from projects.forms import *

from bclabels.utils import check_bclabel_type, assign_bclabel_img, assign_bclabel_svg
from tklabels.utils import check_tklabel_type, assign_tklabel_img, assign_tklabel_svg
from projects.utils import add_to_contributors
from helpers.utils import *
from accounts.utils import get_users_name

from helpers.emails import *

from .forms import *
from .models import *
from .utils import *

# pdfs
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Connect
@login_required(login_url='login')
def connect_community(request):
    community = True
    communities = Community.approved.all()
    form = JoinRequestForm(request.POST or None)

    if request.method == 'POST':
        community_name = request.POST.get('organization_name')
        if Community.objects.filter(community_name=community_name).exists():
            community = Community.objects.get(community_name=community_name)

            # If join request exists or user is already a member, display Error message
            request_exists = JoinRequest.objects.filter(user_from=request.user, community=community).exists()
            user_is_member = community.is_user_in_community(request.user)

            if request_exists or user_is_member:
                messages.add_message(request, messages.ERROR, "Either you have already sent this request or are currently a member of this community.")
                return redirect('connect-community')
            else:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.user_from = request.user
                    data.community = community
                    data.user_to = community.community_creator
                    data.save()

                    # Send community creator email
                    send_join_request_email_admin(request, data, community)
                    messages.add_message(request, messages.SUCCESS, "Request to join community sent!")
                    return redirect('connect-community')
        else:
            messages.add_message(request, messages.ERROR, 'Community not in registry')
            return redirect('connect-community')

    context = { 'community': community, 'communities': communities, 'form': form,}
    return render(request, 'communities/connect-community.html', context)

@login_required(login_url='login')
def preparation_step(request):
    community = True
    return render(request, 'accounts/preparation.html', { 'community' : community })

# Create Community
@login_required(login_url='login')
def create_community(request):
    form = CreateCommunityForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.community_creator = request.user

            # If in test site, approve immediately, skip confirmation step
            if dev_prod_or_local(request.get_host()) == 'DEV':
                data.is_approved = True
                data.save()

                # Add to user affiliations
                affiliation = UserAffiliation.objects.prefetch_related('communities').get(user=request.user)
                affiliation.communities.add(data)
                affiliation.save()

                # Create a Connections instance
                Connections.objects.create(community=data)
                return redirect('dashboard')
            else:
                data.save()

                # Add to user affiliations
                affiliation = UserAffiliation.objects.prefetch_related('communities').get(user=request.user)
                affiliation.communities.add(data)
                affiliation.save()

                # Create a Connections instance
                Connections.objects.create(community=data)
                return redirect('confirm-community', data.id)
    return render(request, 'communities/create-community.html', {'form': form})

# Confirm Community
@login_required(login_url='login')
def confirm_community(request, community_id):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=community_id)

    form = ConfirmCommunityForm(request.POST or None, request.FILES, instance=community)
    if request.method == "POST":
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            send_hub_admins_application_email(request, community, data)
            return redirect('dashboard')
    return render(request, 'accounts/confirm-account.html', {'form': form, 'community': community,})

# Update Community / Settings
@login_required(login_url='login')
def update_community(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role_community(request.user, community)
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
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role_community(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        join_requests_count = JoinRequest.objects.filter(community=community).count()
        form = InviteMemberForm(request.POST or None)
        if request.method == "POST":
            if 'change_member_role_btn' in request.POST:
                current_role = request.POST.get('current_role')
                new_role = request.POST.get('new_role')
                user_id = request.POST.get('user_id')
                member = User.objects.get(id=user_id)
                change_member_role(community, member, current_role, new_role)
                return redirect('members', community.id)
            else:
                receiver = request.POST.get('receiver')
                user_check = is_community_in_user_community(receiver, community)
                
                if user_check == False: # If user is not community member
                    check_invitation = does_community_invite_exist(receiver, community) # Check to see if invitation already exists

                    if check_invitation == False: # If invitation does not exist, save form.
                        if form.is_valid():
                            data = form.save(commit=False)
                            data.sender = request.user
                            data.status = 'sent'
                            data.community = community
                            data.save()
                            # Send email to target user
                            send_community_invite_email(request, data, community)
                            messages.add_message(request, messages.INFO, 'Invitation Sent!')
                            return redirect('members', community.id)
                    else: 
                        messages.add_message(request, messages.INFO, 'The user you are trying to add has already been invited to this community.')
                else:
                    messages.add_message(request, messages.ERROR, 'The user you are trying to add is already a member of this community.')

        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'join_requests_count': join_requests_count,
        }
        return render(request, 'communities/members.html', context)

@login_required(login_url='login')
def member_requests(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    member_role = check_member_role_community(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        join_requests = JoinRequest.objects.filter(community=community)
        if request.method == 'POST':
            selected_role = request.POST.get('selected_role')
            join_request_id = request.POST.get('join_request_id')

            accepted_join_request(community, join_request_id, selected_role)
            return redirect('member-requests', community.id)

        context = {
            'member_role': member_role,
            'community': community,
            'join_requests': join_requests,
        }
        return render(request, 'communities/member-requests.html', context)

@login_required(login_url='login')
def delete_join_request(request, pk, join_id):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    join_request = JoinRequest.objects.get(id=join_id)
    join_request.delete()
    return redirect('member-requests', community.id)

@login_required(login_url='login')
def remove_member(request, pk, member_id):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    member = User.objects.get(id=member_id)
    # what role does member have
    # remove from role
    if member in community.admins.all():
        community.admins.remove(member)
    if member in community.editors.all():
        community.editors.remove(member)
    if member in community.viewers.all():
        community.viewers.remove(member)

    # remove community from userAffiliation instance
    affiliation = UserAffiliation.objects.get(user=member)
    affiliation.communities.remove(community)

    # Delete join request for this community if exists
    if JoinRequest.objects.filter(user_from=member, community=community).exists():
        join_request = JoinRequest.objects.get(user_from=member, community=community)
        join_request.delete()
    
    if '/manage/' in request.META.get('HTTP_REFERER'):
        return redirect('manage-orgs')
    else:
        return redirect('members', community.id)

# Select Labels to Customize
@login_required(login_url='login')
def select_label(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)
    bclabels = BCLabel.objects.select_related('created_by', 'approved_by').prefetch_related('bclabel_translation', 'bclabel_note').filter(community=community)
    tklabels = TKLabel.objects.select_related('created_by', 'approved_by').prefetch_related('tklabel_translation', 'tklabel_note').filter(community=community)

    member_role = check_member_role_community(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        if request.method == "POST":
            bclabel_type = request.POST.get('bclabel-type')
            tklabel_type = request.POST.get('tk-label-type')

            if bclabel_type:
                return redirect('customize-label', community.id, bclabel_type)

            if tklabel_type:
                return redirect('customize-label', community.id, tklabel_type)
        
        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
            'tklabels': tklabels,
        }

        return render(request, 'communities/select-label.html', context)

@login_required(login_url='login')
def customize_label(request, pk, label_type):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role_community(request.user, community)
    if member_role == False or member_role == 'viewer':
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        # TK Label
        if label_type.startswith('tk'):
            tk_type = check_tklabel_type(label_type)
            img_url = assign_tklabel_img(label_type)
            svg_url = assign_tklabel_svg(label_type)

            form = CustomizeTKLabelForm(request.POST or None, request.FILES)

            if request.method == "GET":
                add_translation_formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

            elif request.method == "POST":
                add_translation_formset = AddLabelTranslationFormSet(request.POST)
                label_name = request.POST.get('input-label-name')

                if form.is_valid() and add_translation_formset.is_valid():
                    label_form = form.save(commit=False)
                    label_form.name = label_name
                    label_form.label_type = tk_type
                    label_form.community = community
                    label_form.img_url = img_url
                    label_form.svg_url = svg_url
                    label_form.created_by = request.user
                    label_form.is_approved = False
                    label_form.save()
                    set_language_code(label_form)


                    # Save all label translation instances
                    instances = add_translation_formset.save(commit=False)
                    for instance in instances:
                        instance.tklabel = label_form
                        instance.save()
                        set_language_code(instance)
                    
                    # Create notification
                    name = get_users_name(request.user)
                    title = f"A TK Label was customized by {name} and is waiting approval by another member of the community."
                    ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                    return redirect('select-label', community.id)

        # BCLabel
        if label_type.startswith('bc'):
            bc_type = check_bclabel_type(label_type)
            img_url = assign_bclabel_img(label_type)
            svg_url = assign_bclabel_svg(label_type)

            form = CustomizeBCLabelForm(request.POST or None, request.FILES)

            if request.method == "GET":
                add_translation_formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

            elif request.method == "POST":
                add_translation_formset = AddLabelTranslationFormSet(request.POST)
                label_name = request.POST.get('input-label-name')

                if form.is_valid() and add_translation_formset.is_valid():
                    label_form = form.save(commit=False)
                    label_form.name = label_name
                    label_form.label_type = bc_type
                    label_form.community = community
                    label_form.img_url = img_url
                    label_form.svg_url = svg_url
                    label_form.created_by = request.user
                    label_form.is_approved = False
                    label_form.save()
                    set_language_code(label_form)


                    # Save all label translation instances
                    instances = add_translation_formset.save(commit=False)
                    for instance in instances:
                        instance.bclabel = label_form
                        instance.save()
                        set_language_code(instance)

                    # Send notification
                    name = get_users_name(request.user)
                    title = f"A BC Label was customized by {name} and is waiting approval by another member of the community."
                    ActionNotification.objects.create(community=community, sender=request.user, notification_type="Labels", title=title)

                    return redirect('select-label', community.id)
            
        context = {
            'member_role': member_role,
            'community': community,
            'label_type': label_type,
            'form': form,
            'add_translation_formset': add_translation_formset,
        }
        return render(request, 'communities/customize-label.html', context)

@login_required(login_url='login')
def approve_label(request, pk, label_id):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    bclabel_exists = BCLabel.objects.filter(unique_id=label_id).exists()
    tklabel_exists = TKLabel.objects.filter(unique_id=label_id).exists()

    member_role = check_member_role_community(request.user, community)
    if member_role == False or member_role == 'viewer':
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        bclabel = ''
        tklabel = ''
        if bclabel_exists:
            bclabel = BCLabel.objects.select_related('approved_by').get(unique_id=label_id)
        if tklabel_exists:
            tklabel = TKLabel.objects.select_related('approved_by').get(unique_id=label_id)
        
        form = LabelNoteForm(request.POST or None)
        if request.method == 'POST':
            # If not approved, mark not approved and who it was by
            if 'create_label_note' in request.POST:
                if form.is_valid():
                    data = form.save(commit=False)
                    data.sender = request.user
                    if bclabel:
                        data.bclabel = bclabel
                        data.save()
                        bclabel.is_approved = False
                        bclabel.approved_by = request.user
                        bclabel.save()
                        send_email_label_approved(bclabel)
                    if tklabel:
                        data.tklabel = tklabel
                        data.save()
                        tklabel.is_approved = False
                        tklabel.approved_by = request.user
                        tklabel.save()
                        send_email_label_approved(tklabel)
                    return redirect('select-label', community.id)

            # If approved, save Label
            elif 'approve_label_yes' in request.POST:
                if bclabel:
                    bclabel.is_approved = True
                    bclabel.approved_by = request.user
                    bclabel.save()
                    send_email_label_approved(bclabel)
                if tklabel:
                    tklabel.is_approved = True
                    tklabel.approved_by = request.user
                    tklabel.save()
                    send_email_label_approved(tklabel)
                return redirect('select-label', community.id)
        
        context = {
            'community': community,
            'member_role': member_role,
            'bclabel': bclabel,
            'tklabel': tklabel,
            'form': form,
        }
        return render(request, 'communities/approve-label.html', context)

# Edit Label
@login_required(login_url='login')
def edit_label(request, pk, label_id):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    bclabel = ''
    tklabel = ''
    form = ''
    formset = ''

    member_role = check_member_role_community(request.user, community)
    if member_role == False or member_role == 'viewer':
        return render(request, 'communities/restricted.html', {'community': community})
    else:

        add_translation_formset = AddLabelTranslationFormSet(request.POST or None)
        
        if request.method == 'GET':
            add_translation_formset = AddLabelTranslationFormSet(queryset=LabelTranslation.objects.none())

            if BCLabel.objects.filter(unique_id=label_id).exists():
                bclabel = BCLabel.objects.get(unique_id=label_id)
                form = EditBCLabelForm(instance=bclabel)
                formset = UpdateBCLabelTranslationFormSet(instance=bclabel)

            if TKLabel.objects.filter(unique_id=label_id).exists():
                tklabel = TKLabel.objects.get(unique_id=label_id)
                form = EditTKLabelForm(instance=tklabel)
                formset = UpdateTKLabelTranslationFormSet(instance=tklabel)

        elif request.method == 'POST':
            add_translation_formset = AddLabelTranslationFormSet(request.POST)

            if BCLabel.objects.filter(unique_id=label_id).exists():
                bclabel = BCLabel.objects.get(unique_id=label_id)
                form = EditBCLabelForm(request.POST, request.FILES, instance=bclabel)
                formset = UpdateBCLabelTranslationFormSet(request.POST or None, instance=bclabel)

            if TKLabel.objects.filter(unique_id=label_id).exists():
                tklabel = TKLabel.objects.get(unique_id=label_id)
                form = EditTKLabelForm(request.POST, request.FILES, instance=tklabel)
                formset = UpdateTKLabelTranslationFormSet(request.POST or None, instance=tklabel)


            if form.is_valid() and formset.is_valid() and add_translation_formset.is_valid():
                form.save()
                formset.save()

                # Save all new label translation instances
                instances = add_translation_formset.save(commit=False)
                for instance in instances:
                    if BCLabel.objects.filter(unique_id=label_id).exists():
                        instance.bclabel = bclabel
                    elif TKLabel.objects.filter(unique_id=label_id).exists():
                        instance.tklabel = tklabel

                    instance.save()
                    set_language_code(instance)

                return redirect('select-label', community.id)

        context = {
            'community': community,
            'member_role': member_role,
            'form': form,
            'formset': formset,
            'add_translation_formset': add_translation_formset,
            'bclabel': bclabel,
            'tklabel': tklabel,
        }
        return render(request, 'communities/edit-label.html', context)

@login_required(login_url='login')
def view_label(request, pk, label_uuid):
    community = Community.objects.select_related('community_creator').prefetch_related('admins', 'editors', 'viewers').get(id=pk)

    member_role = check_member_role_community(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        bclabel = ''
        tklabel = ''
        translations = ''
        projects = ''
        creator_name = ''
        approver_name = ''
        bclabels = ''
        tklabels = ''

        if BCLabel.objects.filter(unique_id=label_uuid).exists():
            bclabel = BCLabel.objects.get(unique_id=label_uuid)
            translations = LabelTranslation.objects.filter(bclabel=bclabel)
            projects = bclabel.project_bclabels.all()
            creator_name = get_users_name(bclabel.created_by)
            approver_name = get_users_name(bclabel.approved_by)
            bclabels = BCLabel.objects.filter(community=community).exclude(unique_id=label_uuid)
            tklabels = TKLabel.objects.filter(community=community)
        if TKLabel.objects.filter(unique_id=label_uuid).exists():
            tklabel = TKLabel.objects.get(unique_id=label_uuid)
            translations = LabelTranslation.objects.filter(tklabel=tklabel)
            projects = tklabel.project_tklabels.all()
            creator_name = get_users_name(tklabel.created_by)
            approver_name = get_users_name(tklabel.approved_by)
            tklabels = TKLabel.objects.filter(community=community).exclude(unique_id=label_uuid)
            bclabels = BCLabel.objects.filter(community=community)

        context = {
            'community': community,
            'member_role': member_role,
            'bclabels': bclabels,
            'tklabels': tklabels,
            'bclabel': bclabel,
            'tklabel': tklabel,
            'translations': translations,
            'projects': projects,
            'creator_name': creator_name,
            'approver_name': approver_name,
        }

        return render(request, 'communities/view-label.html', context)


# Projects Main
@login_required(login_url='login')
def projects(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    
    member_role = check_member_role_community(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        # community projects + 
        # projects community has been notified of + 
        # projects where community is contributor
        projects_list = []
        community_projects = community.projects.prefetch_related('bc_labels', 'tk_labels').all()
        for proj in community_projects:
            projects_list.append(proj)

        community_notified = EntitiesNotified.objects.select_related('project').prefetch_related('institutions', 'researchers').filter(communities=community)
        for n in community_notified:
            projects_list.append(n.project)
        
        contribs = ProjectContributors.objects.select_related('project').filter(communities=community)
        for c in contribs:
            projects_list.append(c.project)

        projects = list(set(projects_list))
        
        form = ProjectCommentForm(request.POST or None)

        # Form: Notify project contributor if project was seen
        if request.method == "POST":
            project_uuid = request.POST.get('project-uuid')
            project = Project.objects.select_related('project_creator').prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)

            if "notify-btn" in request.POST:

                if project_uuid != None and project_uuid != 'placeholder':
                    project_status = request.POST.get('project-status')

                    reference_id = project.unique_id
                    statuses = ProjectStatus.objects.filter(project=project, community=community)
                    truncated_project_title = str(project.title)[0:30]

                    title = ''
                    for status in statuses:
                        if project_status == 'seen':
                            status.seen = True
                            status.save()

                            title = community.community_name + ' has seen and acknowledged your Project: ' + truncated_project_title

                        if project_status == 'pending':
                            status.seen = True
                            status.status = 'pending'
                            status.save()

                            title = community.community_name + ' is in the process of applying Labels to your Project: ' + truncated_project_title

                        if project_status == 'not_pending':
                            status.seen = True
                            status.status = 'not_pending'
                            status.save()
                        
                            title = community.community_name + ' will not be applying Labels to your Project: ' + truncated_project_title

                        # Send Notification
                        # TODO: institution notices only??
                        if project.project_notice.exists():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, institution=notice.placed_by_institution, notification_type='Projects', reference_id=reference_id)
                        if project.project_notice.exists():
                            for notice in project.project_notice.all():
                                ActionNotification.objects.create(sender=request.user, title=title, researcher=notice.placed_by_researcher, notification_type='Projects', reference_id=reference_id)
                            
                    return redirect('community-projects', community.id)

            # Form: Add comment to notice
            elif "add-comment-btn" in request.POST:
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
                        if project.project_notice.exists():
                            for notice in project.project_notice.select_related('placed_by_institution', 'placed_by_researcher').all():
                                ActionNotification.objects.create(sender=request.user, title=title, institution=notice.placed_by_institution, notification_type='Projects', reference_id=notice.project.unique_id)
                        if project.project_notice.exists():
                            for notice in project.project_notice.select_related('placed_by_institution', 'placed_by_researcher').all():
                                ActionNotification.objects.create(sender=request.user, title=title, researcher=notice.placed_by_researcher, notification_type='Projects', reference_id=notice.project.unique_id)


                    return redirect('community-projects', community.id)

        context = {
            'member_role': member_role,
            'projects': projects,
            'community': community,
            'form': form,
        }
        return render(request, 'communities/projects.html', context)

# Create Project
@login_required(login_url='login')
def create_project(request, pk):
    community = Community.objects.get(id=pk)

    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    member_role = check_member_role_community(request.user, community)
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

                add_to_contributors(request, contributors, institutions_selected, researchers_selected, data.unique_id)
                
                # Project person formset
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.project = data
                    instance.save()
                    # Send email to added person
                    send_project_person_email(request, instance.email, data.unique_id)

                # Send notification
                truncated_project_title = str(data.title)[0:30]
                name = get_users_name(data.project_creator)
                title = f'A new project was created by {name}: {truncated_project_title} ...'
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
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=community_id)
    project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
    
    member_role = check_member_role_community(request.user, community)
    if member_role == False or member_role == 'viewer': # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        form = EditProjectForm(request.POST or None, instance=project)
        formset = ProjectPersonFormsetInline(request.POST or None, instance=project)
        contributors = ProjectContributors.objects.prefetch_related('institutions', 'researchers', 'communities').get(project=project)

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
                return redirect('community-projects', community.id)

        context = {
            'member_role': member_role,
            'community': community, 
            'project': project, 
            'form': form,
            'formset': formset,
            'contributors': contributors,
        }
        return render(request, 'communities/edit-project.html', context)

@login_required(login_url='login')
def apply_labels(request, pk, project_uuid):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    project = Project.objects.prefetch_related('bc_labels', 'tk_labels').get(unique_id=project_uuid)
    bclabels = BCLabel.objects.select_related('community', 'created_by', 'approved_by').prefetch_related('bclabel_translation', 'bclabel_note').filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.select_related('community', 'created_by', 'approved_by').prefetch_related('tklabel_translation', 'tklabel_note').filter(community=community, is_approved=True)

    notices = project.project_notice.all()
    institution_notices = project.project_institutional_notice.all()

    # Define Notification attrs
    reference_id = str(project.unique_id)
    truncated_project_title = str(project.title)[0:30]
    title = community.community_name + ' has applied Labels to project ' + truncated_project_title + ' ...'

    member_role = check_member_role_community(request.user, community)
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
            
            if notices or institution_notices:
                # add community to project contributors
                contributors = ProjectContributors.objects.get(project=project)
                contributors.communities.add(community)
                contributors.save()
            else:
                comm_title = 'Labels have been applied to the project ' + truncated_project_title + ' ...'
                ActionNotification.objects.create(title=comm_title, notification_type='Projects', community=community, reference_id=reference_id)

            # If Notice exists
            if notices or institution_notices:
                for n in notices:
                    # Archive notice
                    n.archived = True
                    n.save()
                    # send notification to either institution or researcher
                    if n.placed_by_institution:
                        # Add institution to community connections, then add community to institution connections
                        add_to_connections(community, n.placed_by_institution)
                        add_to_connections(n.placed_by_institution, community)
                        ActionNotification.objects.create(title=title, institution=n.placed_by_institution, notification_type='Labels', reference_id=reference_id)
                    if n.placed_by_researcher:
                        # Add researcher to community connections, then add community to researcher connections
                        add_to_connections(community, n.placed_by_researcher)
                        add_to_connections(n.placed_by_researcher, community)
                        ActionNotification.objects.create(title=title, researcher=n.placed_by_researcher, notification_type='Labels', reference_id=reference_id)
                
                for inst_n in institution_notices:
                    inst_n.archived= True
                    inst_n.save()

                    # Notify institution and add to connections
                    add_to_connections(community, inst_n.institution)
                    add_to_connections(inst_n.institution, community)
                    ActionNotification.objects.create(title=title, institution=inst_n.institution, notification_type='Labels', reference_id=reference_id)

            # send email to project creator
            send_email_labels_applied(project, community)
            return redirect('community-projects', community.id)

    context = {
        'member_role': member_role,
        'community': community,
        'project': project,
        'bclabels': bclabels,
        'tklabels': tklabels,
    }
    return render(request, 'communities/apply-labels.html', context)

@login_required(login_url='login')
def connections(request, pk):
    community = Community.objects.select_related('community_creator').get(id=pk)

    member_role = check_member_role_community(request.user, community)
    if member_role == False: # If user is not a member / does not have a role.
        return render(request, 'communities/restricted.html', {'community': community})
    else:
        connections = Connections.objects.get(community=community)

        context = {
            'member_role': member_role,
            'community': community,
            'connections': connections,
        }
        return render(request, 'communities/connections.html', context)

def restricted_view(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    return render(request, 'communities/restricted.html', {'community': community, })

# show community Labels in a PDF
def labels_pdf(request, pk):
    # Get approved labels customized by community
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)
    # combine two querysets
    # labels = list(chain(bclabels,tklabels))

    template_path = 'snippets/pdfs/community-labels.html'
    context = {'community': community, 'bclabels': bclabels, 'tklabels': tklabels,}

    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')

    # if download:
    # response['Content-Disposition'] = 'attachment; filename="labels.pdf"'
    
    # if display
    response['Content-Disposition'] = 'filename="labels.pdf"'

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def download_labels(request, pk):
    community = Community.objects.select_related('community_creator').prefetch_related('projects', 'admins', 'editors', 'viewers').get(id=pk)
    bclabels = BCLabel.objects.filter(community=community, is_approved=True)
    tklabels = TKLabel.objects.filter(community=community, is_approved=True)

    template_path = 'snippets/pdfs/community-labels.html'
    context = {'community': community, 'bclabels': bclabels, 'tklabels': tklabels,}

    files = []

    # Add PDF to zip
    pdf = render_to_pdf(template_path, context)
    files.append(('Labels_Overview.pdf', pdf))

    # Labels Usage guide PDF
    usage_guide_url = 'https://storage.googleapis.com/anth-ja77-local-contexts-8985.appspot.com/guides/LC-TK_BC-Labels-Usage-Guide_2021-11-02.pdf'
    response = requests.get(usage_guide_url) 
    files.append(('BC_TK_Label_Usage_Guide.pdf', response.content))

    # Add Label images, text and translations
    for bclabel in bclabels:
        get_image = requests.get(bclabel.img_url)
        get_svg = requests.get(bclabel.svg_url)
        files.append((bclabel.name + '.png', get_image.content))
        files.append((bclabel.name + '.svg', get_svg.content))

        # Default Label text
        text_content = bclabel.name + '\n' + bclabel.default_text
        text_addon = []

        if bclabel.bclabel_translation.all():
            for translation in bclabel.bclabel_translation.all():
                text_addon.append('\n\n' + translation.title + ' (' + translation.language + ') ' + '\n' + translation.translation)
            files.append((bclabel.name + '.txt', text_content + '\n'.join(text_addon)))
        else:
            files.append((bclabel.name + '.txt', text_content))

    # Add Label images, text and translations
    for tklabel in tklabels:
        get_image = requests.get(tklabel.img_url)
        get_svg = requests.get(tklabel.svg_url)
        files.append((tklabel.name + '.png', get_image.content))
        files.append((tklabel.name + '.svg', get_svg.content))
        
        # Default Label text
        text_content = tklabel.name + '\n' + tklabel.default_text
        text_addon = []

        if tklabel.tklabel_translation.all():
            for translation in tklabel.tklabel_translation.all():
                text_addon.append('\n\n' + translation.title + ' (' + translation.language + ') ' + '\n' + translation.translation)
            files.append((tklabel.name + '.txt', text_content + '\n'.join(text_addon)))
        else:
            files.append((tklabel.name + '.txt', text_content))
    
    # Create Readme
    readme_text = "The Traditional Knowledge (TK) and Biocultural (BC) Labels reinforce the cultural authority and rights of Indigenous communities.\nThe TK and BC Labels are intended to be displayed prominently on public-facing Indigenous community, researcher and institutional websites, metadata and digital collection's pages.\n\nThis folder contains the following files:\n"
    file_names = []
    for f in files:
        file_names.append(f[0])
    readme_content = readme_text + '\n'.join(file_names) + '\n\nRefer to the Usage Guide for details on how to adapt and display the Labels for your community.\n\nFor more information, contact Local Contexts at localcontexts.org or support@localcontexts.org'
    files.append(('README.txt', readme_content))

    # Generate zip file 
    full_zip_in_memory = generate_zip(files)

    response = HttpResponse(full_zip_in_memory, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(community.community_name + '-Labels.zip')

    return response